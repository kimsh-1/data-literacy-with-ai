# -*- coding: utf-8 -*-
"""
cafe_sales 데이터 생성기 (메인 골격 데이터)
- clean: 깨끗한 BI-ready 버전 (xlsx + csv)
- dirty: 함정을 의도적으로 심은 실전 연습 버전 (xlsx + csv)
실행: python gen_cafe_sales.py
산출: ../cafe_sales/cafe_sales_clean.{xlsx,csv}, cafe_sales_dirty.{xlsx,csv}
"""
import os
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)
OUT = os.path.join(os.path.dirname(__file__), "..", "cafe_sales")
os.makedirs(OUT, exist_ok=True)

# ---- 메뉴 마스터 ----
MENU = {
    "커피":   [("아메리카노", 4500), ("카페라떼", 5000), ("카푸치노", 5000), ("바닐라라떼", 5500), ("콜드브루", 5500)],
    "음료":   [("자몽에이드", 6000), ("복숭아아이스티", 5500), ("레몬에이드", 6000), ("딸기라떼", 6500)],
    "디저트": [("치즈케이크", 6500), ("초코머핀", 4000), ("크로플", 5500), ("마카롱", 3000)],
}
STORES = ["강남점", "홍대점"]
PAYMENTS = ["카드", "간편결제", "현금"]

# ---- 기간: 2025-01-01 ~ 2025-06-30 ----
dates = pd.date_range("2025-01-01", "2025-06-30", freq="D")

rows = []
oid = 10001
for d in dates:
    wd = d.weekday()  # 0=Mon
    is_weekend = wd >= 5
    month = d.month
    # 하루 주문량: 주말↑, 여름(6월)↑
    base = 45 if not is_weekend else 70
    base = int(base * (1.0 + 0.04 * (month - 1)))
    n_orders = rng.poisson(base)
    for _ in range(n_orders):
        # 시간대: 오전(8-11), 점심(12-14 피크), 오후(15-18), 저녁(19-21)
        hour = int(rng.choice(
            [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            p=np.array([3, 5, 6, 5, 9, 10, 8, 6, 6, 6, 5, 4, 3, 2], dtype=float)
                / np.sum([3, 5, 6, 5, 9, 10, 8, 6, 6, 6, 5, 4, 3, 2])))
        store = STORES[0] if rng.random() < 0.6 else STORES[1]
        # 여름엔 음료 비중↑
        if month >= 5:
            cat = rng.choice(["커피", "음료", "디저트"], p=[0.45, 0.35, 0.20])
        else:
            cat = rng.choice(["커피", "음료", "디저트"], p=[0.55, 0.18, 0.27])
        item, price = MENU[cat][rng.integers(len(MENU[cat]))]
        qty = int(rng.choice([1, 1, 1, 2, 2, 3], ))
        pay = rng.choice(PAYMENTS, p=[0.62, 0.30, 0.08])
        member = bool(rng.random() < 0.45)
        rows.append({
            "order_id": oid,
            "date": d.strftime("%Y-%m-%d"),
            "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][wd],
            "hour": hour,
            "store": store,
            "category": cat,
            "item": item,
            "unit_price": price,
            "qty": qty,
            "amount": price * qty,
            "payment": pay,
            "member": member,
        })
        oid += 1

clean = pd.DataFrame(rows)

# ---- clean 저장 ----
clean.to_csv(os.path.join(OUT, "cafe_sales_clean.csv"), index=False, encoding="utf-8-sig")
clean.to_excel(os.path.join(OUT, "cafe_sales_clean.xlsx"), index=False, sheet_name="sales")

# ---- dirty 버전: 함정 심기 ----
dirty = clean.copy()
# 결측·문자열 혼입을 허용하려면 해당 컬럼을 object로 (pandas 3.0 엄격 dtype 회피)
dirty["member"] = dirty["member"].astype(object)
dirty["payment"] = dirty["payment"].astype(object)
dirty["unit_price"] = dirty["unit_price"].astype(object)
dirty["qty"] = dirty["qty"].astype(object)
dirty["amount"] = dirty["amount"].astype(object)

# 1) 중복행: 무작위 15건 복제
dup = dirty.sample(15, random_state=SEED)
dirty = pd.concat([dirty, dup], ignore_index=True)

# 2) 결측: payment 3%, member 2% 공백
pay_idx = dirty.sample(frac=0.03, random_state=1).index
dirty.loc[pay_idx, "payment"] = np.nan
mem_idx = dirty.sample(frac=0.02, random_state=2).index
dirty.loc[mem_idx, "member"] = np.nan

# 3) 날짜 형식 혼입: 2% 는 YYYY/MM/DD, 1% 는 M-D-YYYY
d1 = dirty.sample(frac=0.02, random_state=3).index
dirty.loc[d1, "date"] = pd.to_datetime(dirty.loc[d1, "date"]).dt.strftime("%Y/%m/%d")
d2 = dirty.sample(frac=0.01, random_state=4).index
dirty.loc[d2, "date"] = pd.to_datetime(dirty.loc[d2, "date"], format="mixed").dt.strftime("%m-%d-%Y")

# 4) unit_price 문자열 혼입 ("4,500원")
p1 = dirty.sample(frac=0.015, random_state=5).index
dirty.loc[p1, "unit_price"] = dirty.loc[p1, "unit_price"].map(lambda v: f"{int(v):,}원")

# 5) 범주 오타/표기 혼재
o1 = dirty[dirty["item"] == "아메리카노"].sample(frac=0.1, random_state=6).index
dirty.loc[o1, "item"] = rng.choice(["아메리카", "Americano", "아메 리카노"], size=len(o1))
s1 = dirty[dirty["store"] == "강남점"].sample(frac=0.05, random_state=7).index
dirty.loc[s1, "store"] = "강남 점"

# 6) 이상치: qty=999 2건, amount 음수 1건
out_idx = dirty.sample(2, random_state=8).index
dirty.loc[out_idx, "qty"] = 999
neg_idx = dirty.sample(1, random_state=9).index
dirty.loc[neg_idx, "amount"] = -dirty.loc[neg_idx, "amount"].abs()

# 7) 앞뒤 공백
w1 = dirty.sample(frac=0.03, random_state=10).index
dirty.loc[w1, "category"] = " " + dirty.loc[w1, "category"].astype(str) + " "

# 행 순서 섞기(주문번호 순 아님)
dirty = dirty.sample(frac=1.0, random_state=11).reset_index(drop=True)

dirty.to_csv(os.path.join(OUT, "cafe_sales_dirty.csv"), index=False, encoding="utf-8-sig")
dirty.to_excel(os.path.join(OUT, "cafe_sales_dirty.xlsx"), index=False, sheet_name="sales")

# ---- 리포트 ----
print("=== cafe_sales 생성 완료 ===")
print(f"clean: {len(clean):,}행 × {clean.shape[1]}열  기간 {clean['date'].min()}~{clean['date'].max()}")
print(f"       총매출 {clean['amount'].sum():,}원  지점 {clean['store'].unique().tolist()}")
print(f"dirty: {len(dirty):,}행 (중복 15 + 원본)")
print("심은 함정: 중복행 / payment·member 결측 / 날짜형식3종 / unit_price 문자열 / 범주오타 / qty999·음수 / 공백")
print(f"산출 위치: {os.path.abspath(OUT)}")
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    print(f"  - {f}  ({os.path.getsize(p):,} bytes)")
