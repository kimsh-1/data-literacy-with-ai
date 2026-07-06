from __future__ import annotations

import os
import textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "02_datasets"
OUTPUT_DIR = ROOT / "06_answers/S14_outputs"

SUBWAY_PATH = DATA_DIR / "real_korean/seoul_subway/seoulmetro_daily_hourly_2025.csv"
APT_PATH = DATA_DIR / "real_korean/realestate_apt/molit_apt_sale_seoul_gangnam_2024.csv"
CPI_PATH = DATA_DIR / "real_korean/prices_econ/fred_korea_cpi_all_items_monthly.csv"
CAFE_PATH = DATA_DIR / "cafe_sales/cafe_sales_clean.csv"

TIME_COLUMNS = [
    "06시이전",
    "06-07시간대",
    "07-08시간대",
    "08-09시간대",
    "09-10시간대",
    "10-11시간대",
    "11-12시간대",
    "12-13시간대",
    "13-14시간대",
    "14-15시간대",
    "15-16시간대",
    "16-17시간대",
    "17-18시간대",
    "18-19시간대",
    "19-20시간대",
    "20-21시간대",
    "21-22시간대",
    "22-23시간대",
    "23-24시간대",
    "24시이후",
]

FONT_FAMILY = [
    "NanumGothic",
    "NanumGothicCoding",
    "Noto Sans CJK KR",
    "Malgun Gothic",
    "AppleGothic",
    "DejaVu Sans",
    "sans-serif",
]
MONO_FONT_FAMILY = ["D2Coding", "Consolas", "DejaVu Sans Mono", "monospace"]

TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
}

COLOR_FAMILIES = {
    "blue": {
        "open": TOKENS["panel"],
        "xlight": "#EAF1FE",
        "light": "#CEDFFE",
        "base": "#A3BEFA",
        "mid": "#5477C4",
        "dark": "#2E4780",
    },
    "gold": {
        "open": TOKENS["panel"],
        "xlight": "#FFF4C2",
        "light": "#FFEA8F",
        "base": "#FFE15B",
        "mid": "#B8A037",
        "dark": "#736422",
    },
    "orange": {
        "open": TOKENS["panel"],
        "xlight": "#FFEDDE",
        "light": "#FFBDA1",
        "base": "#F0986E",
        "mid": "#CC6F47",
        "dark": "#804126",
    },
    "olive": {
        "open": TOKENS["panel"],
        "xlight": "#D8ECBD",
        "light": "#BEEB96",
        "base": "#A3D576",
        "mid": "#71B436",
        "dark": "#386411",
    },
    "pink": {
        "open": TOKENS["panel"],
        "xlight": "#FCDAD6",
        "light": "#F5BACC",
        "base": "#F390CA",
        "mid": "#BD569B",
        "dark": "#8A3A6F",
    },
}


def require_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{label}에 필요한 컬럼이 없습니다: {sorted(missing)}")


def configure_korean_font() -> str:
    available = {font.name for font in font_manager.fontManager.ttflist}
    selected = next((font for font in FONT_FAMILY if font in available), "DejaVu Sans")

    plt.rcParams["font.family"] = selected
    plt.rcParams["font.sans-serif"] = FONT_FAMILY
    plt.rcParams["font.monospace"] = MONO_FONT_FAMILY
    plt.rcParams["axes.unicode_minus"] = False
    return selected


def use_chart_theme() -> None:
    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": TOKENS["surface"],
            "figure.edgecolor": "none",
            "savefig.facecolor": TOKENS["surface"],
            "savefig.edgecolor": "none",
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "axes.grid": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "grid.color": TOKENS["grid"],
            "grid.linewidth": 0.8,
            "font.family": "sans-serif",
            "font.sans-serif": FONT_FAMILY,
            "font.monospace": MONO_FONT_FAMILY,
            "patch.linewidth": 1.0,
        },
    )
    configure_korean_font()


def add_chart_header(
    fig: plt.Figure,
    ax: plt.Axes,
    title: str,
    subtitle: str,
    *,
    title_width: int = 76,
    subtitle_width: int = 108,
) -> None:
    title = str(title).strip()
    subtitle = str(subtitle).strip()
    if not title or not subtitle:
        raise ValueError("차트에는 제목과 부제가 모두 필요합니다.")

    title_wrapped = textwrap.fill(title, width=title_width, break_long_words=False)
    subtitle_wrapped = textwrap.fill(subtitle, width=subtitle_width, break_long_words=False)
    title_lines = title_wrapped.count("\n") + 1
    subtitle_lines = subtitle_wrapped.count("\n") + 1

    ax.set_title("")
    fig.subplots_adjust(
        top=max(0.62, 0.86 - 0.045 * (title_lines - 1) - 0.032 * (subtitle_lines - 1))
    )

    left = ax.get_position().x0
    fig.text(
        left,
        0.985,
        title_wrapped,
        ha="left",
        va="top",
        fontsize=13,
        fontweight="normal",
        color=TOKENS["ink"],
        linespacing=1.08,
    )
    fig.text(
        left,
        0.93 - 0.045 * (title_lines - 1),
        subtitle_wrapped,
        ha="left",
        va="top",
        fontsize=9,
        color=TOKENS["muted"],
        linespacing=1.18,
    )
    sns.despine(ax=ax)


def format_date_axis(ax: plt.Axes, *, max_ticks: int = 7) -> None:
    locator = mdates.AutoDateLocator(minticks=3, maxticks=max_ticks)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.tick_params(axis="x", labelrotation=0)


def save_figure(fig: plt.Figure, stem: str) -> tuple[Path, Path]:
    png_path = OUTPUT_DIR / f"{stem}.png"
    svg_path = OUTPUT_DIR / f"{stem}.svg"
    fig.savefig(png_path, dpi=160, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, svg_path


def load_subway_heatmap(top_n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subway = pd.read_csv(SUBWAY_PATH)
    require_columns(
        subway,
        {"수송일자", "호선", "역명", "승하차구분", *TIME_COLUMNS},
        "서울 지하철 데이터",
    )

    ride = subway.loc[subway["승하차구분"].eq("승차")].copy()
    ride["역라벨"] = ride["호선"].astype(str) + " " + ride["역명"].astype(str)

    station_hour = ride.groupby("역라벨", observed=True)[TIME_COLUMNS].sum()
    top_stations = station_hour.sum(axis=1).sort_values(ascending=False).head(top_n).index
    heatmap_wide = station_hour.loc[top_stations, TIME_COLUMNS]

    heatmap_long = (
        heatmap_wide.reset_index()
        .melt(id_vars="역라벨", var_name="시간대", value_name="연간승차인원")
        .assign(연간승차인원_백만=lambda df: df["연간승차인원"] / 1_000_000)
    )
    return subway, heatmap_wide, heatmap_long


def plot_subway_heatmap(heatmap_wide: pd.DataFrame) -> tuple[Path, Path]:
    blue = COLOR_FAMILIES["blue"]
    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    sns.heatmap(
        heatmap_wide / 1_000_000,
        ax=ax,
        cmap=sns.light_palette(blue["mid"], as_cmap=True),
        linewidths=0.4,
        linecolor=TOKENS["panel"],
        cbar_kws={"label": "연간 승차인원(백만 명)"},
    )
    ax.set_xlabel("시간대")
    ax.set_ylabel("역")
    ax.tick_params(axis="x", labelrotation=45)
    add_chart_header(
        fig,
        ax,
        "서울 지하철 주요 역의 시간대별 승차 패턴",
        "2025년 승차 기준, 총 승차 상위 10개 역과 20개 시간대를 집계한 히트맵이다.",
    )
    return save_figure(fig, "s14_subway_heatmap")


def load_apartment() -> pd.DataFrame:
    apt = pd.read_csv(APT_PATH)
    require_columns(
        apt,
        {"시군구", "단지명", "전용면적(㎡)", "계약년월", "거래금액(만원)"},
        "강남 아파트 실거래 데이터",
    )
    apt["거래금액_만원"] = pd.to_numeric(
        apt["거래금액(만원)"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )
    apt["거래금액_억원"] = apt["거래금액_만원"] / 10_000
    apt["계약월"] = pd.to_datetime(apt["계약년월"].astype(str), format="%Y%m", errors="coerce")
    apt = apt.dropna(subset=["전용면적(㎡)", "거래금액_만원", "계약월"]).copy()
    apt["면적구간"] = pd.cut(
        apt["전용면적(㎡)"],
        bins=[0, 40, 60, 85, 120, np.inf],
        labels=["40㎡ 이하", "40-60㎡", "60-85㎡", "85-120㎡", "120㎡ 초과"],
        right=True,
    )
    return apt


def plot_apartment_histogram(apt: pd.DataFrame) -> tuple[Path, Path]:
    blue = COLOR_FAMILIES["blue"]
    median_value = apt["거래금액_억원"].median()

    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    sns.histplot(
        data=apt,
        x="거래금액_억원",
        bins=36,
        ax=ax,
        color=blue["base"],
        edgecolor=blue["dark"],
        linewidth=0.8,
    )
    ax.axvline(median_value, color=TOKENS["ink"], linestyle=":", linewidth=1.0)
    ax.text(
        median_value,
        ax.get_ylim()[1] * 0.92,
        f"중앙값 {median_value:,.1f}억원",
        ha="left",
        va="top",
        fontsize=9,
        color=TOKENS["ink"],
    )
    ax.set_xlabel("거래금액(억원)")
    ax.set_ylabel("거래건수")
    add_chart_header(
        fig,
        ax,
        "강남구 아파트 거래금액 분포",
        "2024년 실거래 3,754건 기준, 히스토그램은 값이 어느 구간에 몰려 있는지 보여준다.",
    )
    return save_figure(fig, "s14_apt_price_histogram")


def plot_apartment_boxplot(apt: pd.DataFrame) -> tuple[Path, Path]:
    pink = COLOR_FAMILIES["pink"]
    order = ["40㎡ 이하", "40-60㎡", "60-85㎡", "85-120㎡", "120㎡ 초과"]
    palette = {
        label: pink[tone]
        for label, tone in zip(order, ["xlight", "light", "base", "light", "xlight"])
    }

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    sns.boxplot(
        data=apt,
        x="면적구간",
        y="거래금액_억원",
        hue="면적구간",
        order=order,
        palette=palette,
        dodge=False,
        legend=False,
        linewidth=1.0,
        ax=ax,
    )
    ax.set_xlabel("면적구간")
    ax.set_ylabel("거래금액(억원)")
    add_chart_header(
        fig,
        ax,
        "면적구간별 거래금액의 범위 비교",
        "2024년 강남구 실거래 기준, 박스플롯은 중앙값·분산·이상치를 함께 확인하는 차트다.",
    )
    return save_figure(fig, "s14_apt_area_boxplot")


def plot_apartment_scatter(apt: pd.DataFrame) -> tuple[Path, Path]:
    orange = COLOR_FAMILIES["orange"]
    corr = apt["전용면적(㎡)"].corr(apt["거래금액_만원"])

    fig, ax = plt.subplots(figsize=(9.8, 6.0))
    sns.regplot(
        data=apt,
        x="전용면적(㎡)",
        y="거래금액_억원",
        ci=None,
        scatter_kws={
            "s": 28,
            "alpha": 0.55,
            "color": orange["base"],
            "edgecolor": orange["dark"],
        },
        line_kws={"color": TOKENS["ink"], "linewidth": 1.2},
        ax=ax,
    )
    ax.set_xlabel("전용면적(㎡)")
    ax.set_ylabel("거래금액(억원)")
    add_chart_header(
        fig,
        ax,
        "전용면적이 클수록 거래금액도 높아지는 경향",
        f"2024년 강남구 아파트 실거래 3,754건 기준, 상관계수 r={corr:.3f}. 추세선은 전체 경향을 요약한다.",
    )
    return save_figure(fig, "s14_apt_scatter_trend")


def load_cpi_recent(start: str = "2000-01-01") -> tuple[pd.DataFrame, pd.DataFrame]:
    cpi = pd.read_csv(CPI_PATH)
    require_columns(cpi, {"observation_date", "KORCPIALLMINMEI"}, "FRED CPI 데이터")
    cpi["기준월"] = pd.to_datetime(cpi["observation_date"])
    cpi["소비자물가지수"] = pd.to_numeric(cpi["KORCPIALLMINMEI"], errors="coerce")
    cpi = cpi.dropna(subset=["기준월", "소비자물가지수"]).copy()
    recent = cpi.loc[cpi["기준월"].ge(pd.Timestamp(start)), ["기준월", "소비자물가지수"]].copy()
    return cpi, recent


def plot_cpi_line(cpi_recent: pd.DataFrame) -> tuple[Path, Path]:
    blue = COLOR_FAMILIES["blue"]
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    sns.lineplot(
        data=cpi_recent,
        x="기준월",
        y="소비자물가지수",
        ax=ax,
        color=blue["base"],
        linewidth=1.2,
    )
    ax.set_xlabel("기준월")
    ax.set_ylabel("소비자물가지수")
    format_date_axis(ax, max_ticks=7)
    add_chart_header(
        fig,
        ax,
        "한국 소비자물가지수는 장기적으로 우상향했다",
        "FRED 월별 CPI 지수, 2000년 1월부터 2023년 11월까지의 월별 시계열이다.",
    )
    return save_figure(fig, "s14_cpi_line")


def build_monthly_sales() -> tuple[pd.DataFrame, pd.DataFrame]:
    cafe = pd.read_csv(CAFE_PATH)
    require_columns(cafe, {"date", "order_id", "amount"}, "카페 매출 데이터")
    cafe["date"] = pd.to_datetime(cafe["date"], errors="coerce")
    cafe = cafe.dropna(subset=["date", "amount"]).copy()

    monthly_sales = (
        cafe.groupby(pd.Grouper(key="date", freq="MS"))
        .agg(매출합계=("amount", "sum"), 주문수=("order_id", "count"))
        .reset_index()
        .rename(columns={"date": "월"})
    )
    monthly_sales["객단가"] = monthly_sales["매출합계"] / monthly_sales["주문수"]
    return cafe, monthly_sales


def plot_monthly_sales(monthly_sales: pd.DataFrame) -> tuple[Path, Path]:
    olive = COLOR_FAMILIES["olive"]
    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    sns.lineplot(
        data=monthly_sales,
        x="월",
        y="매출합계",
        marker="o",
        ax=ax,
        color=olive["base"],
        linewidth=1.2,
    )
    ax.set_xlabel("월")
    ax.set_ylabel("매출합계")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x / 1_000_000:.1f}백만"))
    format_date_axis(ax, max_ticks=6)
    add_chart_header(
        fig,
        ax,
        "카페 월별 매출은 6월에 가장 높았다",
        "cafe_sales_clean.csv 기준, 2025년 1월부터 6월까지 월별 매출합계를 집계했다.",
    )
    return save_figure(fig, "s14_monthly_sales_trend")


def write_csv_outputs(
    heatmap_long: pd.DataFrame,
    apt: pd.DataFrame,
    cpi_recent: pd.DataFrame,
    monthly_sales: pd.DataFrame,
) -> dict[str, Path]:
    csv_paths = {
        "subway": OUTPUT_DIR / "s14_subway_station_hour_heatmap.csv",
        "apt": OUTPUT_DIR / "s14_apt_chart_ready.csv",
        "cpi": OUTPUT_DIR / "s14_cpi_recent.csv",
        "monthly_sales": OUTPUT_DIR / "s14_monthly_sales.csv",
    }

    heatmap_long.to_csv(csv_paths["subway"], index=False, encoding="utf-8-sig")
    apt[
        [
            "시군구",
            "단지명",
            "계약월",
            "전용면적(㎡)",
            "거래금액_만원",
            "거래금액_억원",
            "면적구간",
        ]
    ].to_csv(csv_paths["apt"], index=False, encoding="utf-8-sig")
    cpi_recent.to_csv(csv_paths["cpi"], index=False, encoding="utf-8-sig")
    monthly_sales.to_csv(csv_paths["monthly_sales"], index=False, encoding="utf-8-sig")
    return csv_paths


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    use_chart_theme()
    selected_font = configure_korean_font()

    subway, heatmap_wide, heatmap_long = load_subway_heatmap(top_n=10)
    apt = load_apartment()
    cpi_raw, cpi_recent = load_cpi_recent(start="2000-01-01")
    cafe, monthly_sales = build_monthly_sales()

    csv_paths = write_csv_outputs(heatmap_long, apt, cpi_recent, monthly_sales)
    chart_paths = [
        plot_subway_heatmap(heatmap_wide),
        plot_apartment_histogram(apt),
        plot_apartment_boxplot(apt),
        plot_apartment_scatter(apt),
        plot_cpi_line(cpi_recent),
        plot_monthly_sales(monthly_sales),
    ]

    apt_corr = apt["전용면적(㎡)"].corr(apt["거래금액_만원"])

    print("S14 검증 결과")
    print(f"pandas version: {pd.__version__}")
    print(f"matplotlib version: {matplotlib.__version__}")
    print(f"seaborn version: {sns.__version__}")
    print(f"selected font: {selected_font}")
    print()
    print("[데이터 행수]")
    print(f"서울 지하철 원자료: {len(subway):,}행")
    print(f"서울 지하철 승차 집계 heatmap CSV: {len(heatmap_long):,}행")
    print(f"강남 아파트 원자료 및 분석 가능 행수: {len(pd.read_csv(APT_PATH)):,}행 / {len(apt):,}행")
    print(f"FRED CPI 원자료 및 2000년 이후 시계열: {len(cpi_raw):,}행 / {len(cpi_recent):,}행")
    print(f"카페 매출 원자료 및 월별 집계: {len(cafe):,}행 / {len(monthly_sales):,}행")
    print()
    print("[핵심 확인값]")
    print(f"아파트 전용면적-거래금액 상관계수 r: {apt_corr:.3f}")
    print(
        "카페 월별 매출 범위: "
        f"{monthly_sales['매출합계'].min():,.0f}원~{monthly_sales['매출합계'].max():,.0f}원"
    )
    print()
    print("[저장한 CSV]")
    for label, path in csv_paths.items():
        print(f"{label}: {path}")
    print()
    print("[저장한 차트]")
    for png_path, svg_path in chart_paths:
        print(f"{png_path}")
        print(f"{svg_path}")
    print("검증 통과")


if __name__ == "__main__":
    main()
