from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
APT_PATH = ROOT / "02_datasets/real_korean/realestate_apt/molit_apt_sale_seoul_gangnam_2024.csv"
CAFE_RESTAURANT_PATH = (
    ROOT / "02_datasets/real_korean/cafe_restaurant/seoul_commercial_food_stores_202109_github.csv"
)
OUTPUT_DIR = ROOT / "06_answers/S20_outputs"


def format_manwon(value: float) -> str:
    return f"{value:,.0f}만원"


def load_apartment() -> pd.DataFrame:
    apt = pd.read_csv(APT_PATH)
    required = {"전용면적(㎡)", "거래금액(만원)", "계약년월", "시군구", "단지명"}
    missing = required - set(apt.columns)
    if missing:
        raise ValueError(f"아파트 데이터에 필요한 컬럼이 없습니다: {sorted(missing)}")

    apt["거래금액_만원"] = pd.to_numeric(
        apt["거래금액(만원)"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )
    apt["계약월"] = pd.to_datetime(apt["계약년월"].astype(str), format="%Y%m", errors="coerce")
    usable = apt.dropna(subset=["전용면적(㎡)", "거래금액_만원", "계약월"]).copy()
    return usable


def relationship_stats(df: pd.DataFrame) -> dict[str, float | str]:
    x = df["전용면적(㎡)"]
    y = df["거래금액_만원"]
    x_mean = x.mean()
    y_mean = y.mean()
    slope = ((x - x_mean) * (y - y_mean)).sum() / ((x - x_mean) ** 2).sum()
    intercept = y_mean - slope * x_mean
    corr = x.corr(y)
    if corr >= 0.7:
        strength = "강한 양의 상관"
    elif corr >= 0.3:
        strength = "보통 수준의 양의 상관"
    elif corr > 0:
        strength = "약한 양의 상관"
    elif corr == 0:
        strength = "뚜렷한 선형 상관 없음"
    else:
        strength = "음의 상관"
    return {
        "corr": corr,
        "slope": slope,
        "intercept": intercept,
        "strength": strength,
    }


def build_apartment_outputs(df: pd.DataFrame) -> dict[str, object]:
    relationship = relationship_stats(df)

    area_bins = [0, 40, 60, 85, 120, 1000]
    area_labels = ["40㎡ 이하", "40-60㎡", "60-85㎡", "85-120㎡", "120㎡ 초과"]
    grouped = df.copy()
    grouped["면적구간"] = pd.cut(
        grouped["전용면적(㎡)"],
        bins=area_bins,
        labels=area_labels,
        right=True,
    )

    area_summary = (
        grouped.groupby("면적구간", observed=True)
        .agg(
            거래건수=("거래금액_만원", "size"),
            중앙값_만원=("거래금액_만원", "median"),
            평균_만원=("거래금액_만원", "mean"),
            최소_만원=("거래금액_만원", "min"),
            최대_만원=("거래금액_만원", "max"),
        )
        .reset_index()
    )

    monthly_summary = (
        df.groupby("계약월")
        .agg(
            거래건수=("거래금액_만원", "size"),
            중앙값_만원=("거래금액_만원", "median"),
        )
        .reset_index()
    )
    monthly_summary["계약월"] = monthly_summary["계약월"].dt.strftime("%Y-%m")

    same_area = df[(df["전용면적(㎡)"] >= 80) & (df["전용면적(㎡)"] < 90)].copy()
    same_area_summary = {
        "count": int(len(same_area)),
        "median": float(same_area["거래금액_만원"].median()),
        "min": float(same_area["거래금액_만원"].min()),
        "max": float(same_area["거래금액_만원"].max()),
        "complex_count": int(same_area["단지명"].nunique()),
        "dong_count": int(same_area["시군구"].nunique()),
    }
    same_area_by_dong = (
        same_area.groupby("시군구")
        .agg(
            거래건수=("거래금액_만원", "size"),
            중앙값_만원=("거래금액_만원", "median"),
            최소_만원=("거래금액_만원", "min"),
            최대_만원=("거래금액_만원", "max"),
        )
        .sort_values("중앙값_만원", ascending=False)
        .reset_index()
    )

    return {
        "relationship": relationship,
        "area_summary": area_summary,
        "monthly_summary": monthly_summary,
        "same_area_summary": same_area_summary,
        "same_area_by_dong": same_area_by_dong,
    }


def load_cafe_restaurant_summary() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cafe = pd.read_csv(CAFE_RESTAURANT_PATH)
    required = {"시군구명", "상권업종중분류명"}
    missing = required - set(cafe.columns)
    if missing:
        raise ValueError(f"상권 데이터에 필요한 컬럼이 없습니다: {sorted(missing)}")

    top_gu = (
        cafe.groupby("시군구명")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="점포수")
    )
    top_category = (
        cafe.groupby("상권업종중분류명")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="점포수")
    )
    top_gu_category = (
        cafe.groupby(["시군구명", "상권업종중분류명"])
        .size()
        .reset_index(name="점포수")
        .sort_values("점포수", ascending=False)
        .head(10)
    )
    return cafe, top_gu, top_category, top_gu_category


def write_one_page_report(
    cafe: pd.DataFrame,
    top_gu: pd.DataFrame,
    top_category: pd.DataFrame,
    top_gu_category: pd.DataFrame,
) -> Path:
    report_path = OUTPUT_DIR / "s20_one_page_report_example.md"
    gu_1, gu_2, gu_3 = top_gu.iloc[0], top_gu.iloc[1], top_gu.iloc[2]
    category_1, category_2 = top_category.iloc[0], top_category.iloc[1]
    gu_category_1 = top_gu_category.iloc[0]
    gu_category_2 = top_gu_category.iloc[1]
    gu_category_3 = top_gu_category.iloc[2]
    gu_category_4 = top_gu_category.iloc[3]

    report_text = f"""# S20 1페이지 인사이트 보고서 예시

## 제목
서울 음식점·카페 상권은 {gu_1["시군구명"]}에 가장 집중되어 있으며, 구별 우선순위는 {category_1["상권업종중분류명"]}과 {category_2["상권업종중분류명"]} 조합부터 확인해야 한다.

## 발견
- 분석 대상은 서울 음식점·카페 상권 데이터 {len(cafe):,}행이다.
- 구별 점포수는 {gu_1["시군구명"]} {gu_1["점포수"]:,}개, {gu_2["시군구명"]} {gu_2["점포수"]:,}개, {gu_3["시군구명"]} {gu_3["점포수"]:,}개 순으로 많다.
- 업종별 점포수는 {category_1["상권업종중분류명"]} {category_1["점포수"]:,}개, {category_2["상권업종중분류명"]} {category_2["점포수"]:,}개가 상위에 온다.
- 구별·업종 조합은 {gu_category_1["시군구명"]} {gu_category_1["상권업종중분류명"]} {gu_category_1["점포수"]:,}개, {gu_category_2["시군구명"]} {gu_category_2["상권업종중분류명"]} {gu_category_2["점포수"]:,}개, {gu_category_3["시군구명"]} {gu_category_3["상권업종중분류명"]} {gu_category_3["점포수"]:,}개, {gu_category_4["시군구명"]} {gu_category_4["상권업종중분류명"]} {gu_category_4["점포수"]:,}개가 상위에 온다.

## 시사점
상권 후보를 고를 때는 전체 점포수가 많은 구를 먼저 보되, 실제 실행 우선순위는 업종별 밀집도까지 함께 보아야 한다. {gu_1["시군구명"]}는 전체 점포수와 주요 업종 점포수가 모두 높으므로 1차 조사 후보로 적합하다.

## 권장 액션
1. 상권 조사 담당자는 {gu_1["시군구명"]}, {gu_2["시군구명"]}, {gu_3["시군구명"]}를 1차 비교 대상으로 잡는다.
2. 각 구는 {category_1["상권업종중분류명"]}과 {category_2["상권업종중분류명"]} 점포수를 먼저 비교하고, 경쟁 강도가 높은 조합을 표시한다.
3. 보고서에는 구별 점포수 막대그래프 1개와 구별·업종 상위 10개 표 1개만 남기고, 원자료 전체 표는 부록으로 보낸다.

## 시각화 선택
- 핵심 차트: 구별·업종 조합 상위 10개 막대그래프
- 보조 표: 구별 점포수 상위 10개

## 주의
이 결과는 교육용 데이터 분석 예시이며, 실제 출점 판단은 임대료, 유동인구, 매출, 배달 수요, 폐업률, 접근성 같은 추가 정보와 함께 검토해야 한다.
"""
    report_path.write_text(report_text, encoding="utf-8")
    return report_path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cafe, top_gu, top_category, top_gu_category = load_cafe_restaurant_summary()
    report_path = write_one_page_report(cafe, top_gu, top_category, top_gu_category)
    top_gu.to_csv(OUTPUT_DIR / "s20_cafe_top_gu.csv", index=False, encoding="utf-8")
    top_gu_category.to_csv(
        OUTPUT_DIR / "s20_cafe_top_gu_category.csv", index=False, encoding="utf-8"
    )

    apt = load_apartment()
    apt_outputs = build_apartment_outputs(apt)
    apt_outputs["area_summary"].to_csv(
        OUTPUT_DIR / "s20_area_summary.csv", index=False, encoding="utf-8"
    )
    apt_outputs["monthly_summary"].to_csv(
        OUTPUT_DIR / "s20_monthly_summary.csv", index=False, encoding="utf-8"
    )
    apt_outputs["same_area_by_dong"].to_csv(
        OUTPUT_DIR / "s20_80_90sqm_by_dong.csv", index=False, encoding="utf-8"
    )

    relationship = apt_outputs["relationship"]
    same_area = apt_outputs["same_area_summary"]

    print("S20 검증 결과")
    print(f"pandas version: {pd.__version__}")
    print()

    print("[1] S19 상권 구별·업종 점포수 결과물 재현")
    print(f"파일: {CAFE_RESTAURANT_PATH}")
    print(f"원자료 행수: {len(cafe):,}행")
    print("구별 점포수 상위 3개")
    print(top_gu.head(3).to_string(index=False))
    print()
    print("구별·업종 조합 상위 4개")
    print(top_gu_category.head(4).to_string(index=False))
    print()

    print("[2] 강남 아파트 대안 예시 확인")
    print(f"파일: {APT_PATH}")
    print(f"원자료 행수: {len(pd.read_csv(APT_PATH)):,}행")
    print(f"분석 가능 행수: {len(apt):,}행")
    print("확인 컬럼: 전용면적(㎡), 거래금액(만원), 계약년월, 시군구, 단지명")
    print(
        "전용면적-거래금액 산점도와 추세선 해석: "
        f"{relationship['strength']}, 상관계수 {relationship['corr']:.3f}"
    )
    print(
        "80-90㎡ 거래: "
        f"{same_area['count']:,}행, 중앙값 {format_manwon(same_area['median'])}, "
        f"범위 {format_manwon(same_area['min'])}~{format_manwon(same_area['max'])}"
    )
    print()

    print("[3] 저장한 S20 답안 보조 산출물")
    print(f"보고서 예시: {report_path}")
    print(f"상권 구별 요약: {OUTPUT_DIR / 's20_cafe_top_gu.csv'}")
    print(f"상권 구별·업종별 요약: {OUTPUT_DIR / 's20_cafe_top_gu_category.csv'}")
    print(f"아파트 대안 면적 구간 요약: {OUTPUT_DIR / 's20_area_summary.csv'}")
    print(f"아파트 대안 월별 요약: {OUTPUT_DIR / 's20_monthly_summary.csv'}")
    print(f"아파트 대안 80-90㎡ 동별 요약: {OUTPUT_DIR / 's20_80_90sqm_by_dong.csv'}")


if __name__ == "__main__":
    main()
