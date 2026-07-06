#!/usr/bin/env python3
"""Procedural calm-rising cinematic BGM bed for the 30s intro.
Credential-free fallback: pure numpy synthesis -> WAV. No ML deps.
Shapes a I-V-vi-IV progression with pads + sub bass + late arpeggio + gentle
pulse, over an amplitude arc that rises from calm to confident across 30s."""
import numpy as np, wave, struct, sys

SR = 44100
DUR = 30.5              # a hair over 30 so the fade-out clears 30.0
N = int(SR * DUR)
t = np.arange(N) / SR

# ---- note table ----
def hz(n):  # midi-ish name -> freq via A4=440
    names = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
    p = names[n[:-1]]; octv = int(n[-1])
    midi = 12*(octv+1)+p
    return 440.0 * 2**((midi-69)/12)

# Progression: C - G/B - Am - F  (I - V - vi - IV), warm smooth voice-leading.
# Each chord: (pad voicing, bass root)
prog = [
    (['C4','E4','G4'], 'C2'),
    (['B3','D4','G4'], 'G1'),
    (['C4','E4','A4'], 'A1'),
    (['C4','F4','A4'], 'F1'),
]
CHORD = 3.75           # seconds per chord -> 8 chords over 30s
seq = (prog + prog)    # 8 chords

def adsr(dur_s, a=0.9, r=1.2):
    n = int(dur_s*SR); env = np.ones(n)
    na = int(a*SR); nr = int(r*SR)
    if na>0: env[:na] = np.linspace(0,1,na)
    if nr>0: env[-nr:] = np.linspace(1,0,nr)
    return env

def pad_tone(freq, dur_s, detune=0.004):
    n = int(dur_s*SR); tt = np.arange(n)/SR
    # warm additive: fundamental + soft harmonics, two slightly detuned voices
    sig = np.zeros(n)
    for mul,amp in [(1,1.0),(2,0.32),(3,0.14),(4,0.06)]:
        lfo = 1 + 0.0025*np.sin(2*np.pi*(0.15+0.03*mul)*tt)
        sig += amp*np.sin(2*np.pi*freq*mul*tt*lfo)
        sig += amp*np.sin(2*np.pi*freq*mul*(1+detune)*tt)
    return sig/ np.max(np.abs(sig)+1e-9)

pad = np.zeros(N); bass = np.zeros(N); arp = np.zeros(N); pulse = np.zeros(N)
xfade = int(0.6*SR)

for i,(voi,root) in enumerate(seq):
    start = int(i*CHORD*SR)
    dur = CHORD + 0.7      # overlap into next for smooth crossfade
    env = adsr(dur, a=1.0, r=1.0)
    seg = np.zeros(len(env))
    for name in voi:
        seg += pad_tone(hz(name), dur)
    seg = seg/len(voi) * env
    end = min(N, start+len(seg))
    pad[start:end] += seg[:end-start] * 0.55
    # sub bass — soft sine + light 2nd harmonic
    bt = np.arange(end-start)/SR
    bf = hz(root)
    bseg = (np.sin(2*np.pi*bf*bt) + 0.25*np.sin(2*np.pi*2*bf*bt)) * adsr(dur, a=0.6, r=1.0)[:end-start]
    bass[start:end] += bseg * 0.5

# ---- arpeggio: enters ~9s, soft triangle notes, chord tones up an octave ----
arp_start = 9.0
step = CHORD/6.0     # 6 notes per chord
for i,(voi,root) in enumerate(seq):
    cstart = i*CHORD
    tones = [hz(voi[0])*2, hz(voi[1])*2, hz(voi[2])*2, hz(voi[1])*2, hz(voi[2])*2, hz(voi[0])*4]
    for k in range(6):
        ns = cstart + k*step
        if ns < arp_start: continue
        s = int(ns*SR); ln = int(step*0.95*SR)
        e = min(N, s+ln)
        if e<=s: continue
        tt = np.arange(e-s)/SR
        f = tones[k]
        # soft plucked-ish: sine with quick decay
        env = np.exp(-3.5*tt) * (1-np.exp(-80*tt))
        note = (np.sin(2*np.pi*f*tt) + 0.15*np.sin(2*np.pi*2*f*tt)) * env
        arp[s:e] += note * 0.16

# ---- gentle pulse: soft low sine thump on the beat, enters ~15s ----
pulse_start = 15.0
beat = CHORD/4.0   # quarter notes
nb = int(DUR/beat)
for b in range(nb):
    bs = b*beat
    if bs < pulse_start: continue
    s = int(bs*SR); ln = int(0.22*SR); e = min(N, s+ln)
    tt = np.arange(e-s)/SR
    env = np.exp(-14*tt)
    thump = np.sin(2*np.pi*(55*np.exp(-8*tt))*tt) * env
    pulse[s:e] += thump * 0.20

# ---- master amplitude arc: calm -> confident ----
arc = 0.45 + 0.55*np.clip((t/26.0),0,1)**0.85          # rise to full by ~26s
arc *= (1 - 0.15*np.exp(-((t-13)**2)/6.0))              # subtle breath dip mid
mix = (pad*arc + bass*(0.55+0.45*arc) + arp*arc*1.1 + pulse*arc)

# fade in / out
fin = int(0.6*SR); fout = int(2.2*SR)
mix[:fin] *= np.linspace(0,1,fin)
mix[-fout:] *= np.linspace(1,0,fout)**1.3

# normalize
mix = mix / (np.max(np.abs(mix))+1e-9) * 0.92
stereo = np.stack([mix, mix], axis=1)
# tiny stereo widening on pads via short delay
d = int(0.008*SR)
stereo[d:,1] = 0.5*stereo[d:,1] + 0.5*mix[:-d]

pcm = (stereo*32767).astype('<i2')
out = sys.argv[1] if len(sys.argv)>1 else 'assets/bgm/track_raw.wav'
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', out, 'frames', len(mix), 'dur', len(mix)/SR)
