from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "02_datasets" / "real_korean" / "cafe_restaurant" / "seoul_commercial_food_stores_202109_github.csv"
OUT_DIR = ROOT / "06_answers" / "S19_outputs"

GU_SUMMARY_PATH = OUT_DIR / "S19_gu_summary.csv"
BI_INPUT_PATH = OUT_DIR / "S19_bi_input_gu_category.csv"
AI_INPUT_PATH = OUT_DIR / "S19_ai_summary_input.txt"
CHART_PATH = OUT_DIR / "S19_python_top10_gu_chart.png"


def set_korean_font() -> None:
    """실습 환경에 있는 한글 폰트를 우선 사용한다."""
    candidates = [
        "NanumGothic",
        "NanumBarunGothic",
        "NanumGothicCoding",
        "Noto Sans CJK KR",
        "Noto Sans KR",
        "Malgun Gothic",
        "AppleGothic",
    ]
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    set_korean_font()

    df = pd.read_csv(DATA_PATH)
    required_cols = [
        "상가업소번호",
        "상호명",
        "상권업종중분류명",
        "시도명",
        "시군구명",
        "행정동명",
        "경도",
        "위도",
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"필수 컬럼이 없습니다: {missing_cols}")

    raw_rows, raw_cols = df.shape
    required_missing = df[required_cols].isna().sum()
    duplicate_store_ids = int(df["상가업소번호"].duplicated().sum())

    work = df[required_cols].copy()
    work = work[work["시도명"].eq("서울특별시")].copy()
    work["상호명"] = work["상호명"].fillna("(상호명 없음)")

    gu_summary = (
        work.groupby("시군구명")
        .agg(
            점포수=("상가업소번호", "count"),
            중분류수=("상권업종중분류명", "nunique"),
            행정동수=("행정동명", "nunique"),
            평균경도=("경도", "mean"),
            평균위도=("위도", "mean"),
        )
        .reset_index()
    )

    cafe_counts = (
        work[work["상권업종중분류명"].eq("커피점/카페")]
        .groupby("시군구명")
        .size()
        .rename("카페점포수")
    )
    korean_food_counts = (
        work[work["상권업종중분류명"].eq("한식")]
        .groupby("시군구명")
        .size()
        .rename("한식점포수")
    )

    gu_summary = (
        gu_summary.merge(cafe_counts, on="시군구명", how="left")
        .merge(korean_food_counts, on="시군구명", how="left")
        .fillna({"카페점포수": 0, "한식점포수": 0})
    )
    gu_summary["카페점포수"] = gu_summary["카페점포수"].astype(int)
    gu_summary["한식점포수"] = gu_summary["한식점포수"].astype(int)
    gu_summary["카페비율"] = gu_summary["카페점포수"] / gu_summary["점포수"]
    gu_summary["한식비율"] = gu_summary["한식점포수"] / gu_summary["점포수"]
    gu_summary = gu_summary.sort_values("점포수", ascending=False)
    gu_summary.to_csv(GU_SUMMARY_PATH, index=False, encoding="utf-8-sig")

    bi_input = (
        work.groupby(["시군구명", "상권업종중분류명"])
        .size()
        .rename("점포수")
        .reset_index()
        .sort_values(["시군구명", "점포수"], ascending=[True, False])
    )
    bi_input["구내비율"] = bi_input["점포수"] / bi_input.groupby("시군구명")["점포수"].transform("sum")
    bi_input["전체대비비율"] = bi_input["점포수"] / len(work)
    bi_input.to_csv(BI_INPUT_PATH, index=False, encoding="utf-8-sig")

    top10 = gu_summary.head(10).copy()
    top10_for_plot = top10.sort_values("점포수", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top10_for_plot["시군구명"], top10_for_plot["점포수"], color="#3B7D7A")
    ax.set_title("서울 음식 업종 점포 수 상위 10개 구")
    ax.set_xlabel("점포 수")
    ax.set_ylabel("시군구")
    ax.set_xlim(0, top10_for_plot["점포수"].max() * 1.22)
    ax.grid(axis="x", linestyle="--", alpha=0.25)

    for bar, count, cafe_rate in zip(bars, top10_for_plot["점포수"], top10_for_plot["카페비율"]):
        ax.text(
            count + top10_for_plot["점포수"].max() * 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{count:,}개 / 카페 {cafe_rate:.1%}",
            va="center",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(CHART_PATH, dpi=160, bbox_inches="tight")
    plt.close(fig)

    mid_category_counts = work["상권업종중분류명"].value_counts().head(8)
    ai_text = "\n".join(
        [
            "[S19 AI 요약 입력용 집계]",
            f"- 원자료: {raw_rows:,}행 x {raw_cols:,}열",
            f"- 서울특별시 필터 후 분석 행수: {len(work):,}행",
            f"- 시군구 수: {work['시군구명'].nunique():,}개",
            f"- 업종 중분류 수: {work['상권업종중분류명'].nunique():,}개",
            f"- 상가업소번호 중복 수: {duplicate_store_ids:,}건",
            "- 필수 컬럼 결측 수:",
            required_missing.to_string(),
            "",
            "[점포 수 상위 10개 구]",
            top10[
                ["시군구명", "점포수", "카페점포수", "카페비율", "한식점포수", "한식비율"]
            ].to_string(index=False, formatters={"카페비율": "{:.1%}".format, "한식비율": "{:.1%}".format}),
            "",
            "[업종 중분류 상위 8개]",
            mid_category_counts.to_string(),
        ]
    )
    AI_INPUT_PATH.write_text(ai_text, encoding="utf-8")

    print(f"pandas: {pd.__version__}")
    print(f"원자료: {raw_rows:,}행 x {raw_cols:,}열")
    print(f"분석 행수: {len(work):,}행")
    print(f"시군구 수: {work['시군구명'].nunique():,}개")
    print(f"업종 중분류 수: {work['상권업종중분류명'].nunique():,}개")
    print(f"상가업소번호 중복 수: {duplicate_store_ids:,}건")
    print(f"BI 입력 CSV: {bi_input.shape[0]:,}행 x {bi_input.shape[1]:,}열")
    print(f"1위 구: {top10.iloc[0]['시군구명']} {int(top10.iloc[0]['점포수']):,}개")
    print(f"전체 커피점/카페: {int((work['상권업종중분류명'] == '커피점/카페').sum()):,}개")
    print(f"저장: {GU_SUMMARY_PATH.relative_to(ROOT)}")
    print(f"저장: {BI_INPUT_PATH.relative_to(ROOT)}")
    print(f"저장: {AI_INPUT_PATH.relative_to(ROOT)}")
    print(f"저장: {CHART_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
