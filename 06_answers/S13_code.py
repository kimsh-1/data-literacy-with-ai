from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "02_datasets"


def print_table(title: str, df: pd.DataFrame, max_rows: int | None = None) -> None:
    print(f"\n[{title}]")
    if max_rows is not None:
        df = df.head(max_rows)
    print(df.to_string(index=False))


def build_shop_order_analysis() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    orders = pd.read_csv(DATA / "shop_orders/orders.csv")
    customers = pd.read_csv(DATA / "shop_orders/customers.csv")
    products = pd.read_csv(DATA / "shop_orders/products.csv")

    print("[데이터 행수 확인]")
    print(f"orders: {len(orders):,}행, {orders.shape[1]}열")
    print(f"customers: {len(customers):,}행, {customers.shape[1]}열")
    print(f"products: {len(products):,}행, {products.shape[1]}열")

    merged = (
        orders.merge(customers, on="customer_id", how="left")
        .merge(products, on="product_id", how="left")
    )

    merge_nulls = merged[["region", "category", "price"]].isna().sum()
    assert len(merged) == len(orders)
    assert int(merge_nulls.sum()) == 0

    merged["sales"] = merged["price"] * merged["qty"] * (1 - merged["discount_rate"])

    region_category_summary = (
        merged.groupby(["region", "category"])
        .agg(
            주문건수=("order_id", "nunique"),
            판매수량=("qty", "sum"),
            매출합계=("sales", "sum"),
            평균주문금액=("sales", "mean"),
        )
        .reset_index()
        .sort_values("매출합계", ascending=False)
    )

    region_category_display = region_category_summary.copy()
    for col in ["매출합계", "평균주문금액"]:
        region_category_display[col] = region_category_display[col].round(0).astype("int64")

    pivot = pd.pivot_table(
        merged,
        index="region",
        columns="category",
        values="sales",
        aggfunc="sum",
        fill_value=0,
        margins=True,
        margins_name="합계",
    )
    pivot_display = pivot.round(0).astype("int64")

    assert abs(merged["sales"].sum() - 1_938_489_803.0) < 0.1
    assert region_category_summary.iloc[0]["region"] == "서울특별시"
    assert region_category_summary.iloc[0]["category"] == "디지털"

    print(f"병합 후: {len(merged):,}행, {merged.shape[1]}열")
    print(f"병합 누락값 합계: {int(merge_nulls.sum())}")
    print(f"전체 매출 합계: {merged['sales'].sum():,.0f}")
    print_table("지역 x 카테고리 집계 상위 10개", region_category_display, 10)
    print("\n[지역 x 카테고리 피벗 테이블 일부]")
    print(pivot_display.head().to_string())

    return merged, region_category_summary, pivot_display


def build_population_melt_demo() -> pd.DataFrame:
    pop = pd.read_csv(
        DATA / "real_korean/population_kosis/mois_legal_dong_gender_age_population_20260531.csv"
    )

    id_cols = ["법정동코드", "기준연월", "시도명", "시군구명", "읍면동명", "리명"]
    age_gender_cols = [
        col
        for col in pop.columns
        if (col.endswith("남자") or col.endswith("여자")) and col not in ["남자", "여자"]
    ]

    seoul_pop = pop[pop["시도명"] == "서울특별시"].copy()
    long_pop = seoul_pop.melt(
        id_vars=id_cols,
        value_vars=age_gender_cols,
        var_name="연령성별",
        value_name="인구수",
    )
    long_pop["성별"] = long_pop["연령성별"].str.extract("(남자|여자)$")
    long_pop["연령"] = (
        long_pop["연령성별"].str.replace("(남자|여자)$", "", regex=True).str.strip()
    )

    assert pop.shape == (18_623, 231)
    assert len(age_gender_cols) == 222
    assert len(seoul_pop) == 452
    assert len(long_pop) == 100_344
    assert int(long_pop["인구수"].sum()) == int(seoul_pop["남자"].sum() + seoul_pop["여자"].sum())

    print("\n[wide -> long 확인]")
    print(f"원본 인구 파일: {len(pop):,}행, {pop.shape[1]}열")
    print(f"서울특별시 wide: {len(seoul_pop):,}행, {seoul_pop.shape[1]}열")
    print(f"melt 대상 연령/성별 열: {len(age_gender_cols):,}개")
    print(f"서울특별시 long: {len(long_pop):,}행, {long_pop.shape[1]}열")
    print_table(
        "melt 결과 일부",
        long_pop[["시도명", "시군구명", "읍면동명", "연령성별", "연령", "성별", "인구수"]],
        8,
    )

    return long_pop


def build_store_top10() -> pd.DataFrame:
    stores = pd.read_csv(
        DATA / "real_korean/cafe_restaurant/seoul_commercial_food_stores_202109_github.csv"
    )

    top10 = (
        stores.groupby("상권업종중분류명")
        .size()
        .reset_index(name="업소수")
        .sort_values("업소수", ascending=False)
        .head(10)
    )

    assert stores.shape == (119_158, 13)
    assert top10.iloc[0]["상권업종중분류명"] == "한식"
    assert int(top10.iloc[0]["업소수"]) == 40_448

    print("\n[서울 음식점 상권 업종 상위 10개]")
    print(f"상가업소 파일: {len(stores):,}행, {stores.shape[1]}열")
    print_table("중분류 기준 상위 10개", top10)

    return top10


def solve_living_population_mission() -> pd.DataFrame:
    living = pd.read_csv(
        DATA / "real_korean/seoul_living_pop/seoul_living_population_gu_daily.csv"
    )
    original_shape = living.shape
    living["기준일"] = pd.to_datetime(living["기준일ID"].astype(str), format="%Y%m%d")

    gu_living = living[living["시군구명"] != "서울시"].copy()
    gu_summary = (
        gu_living.groupby("시군구명")
        .agg(
            관측일수=("기준일", "nunique"),
            평균생활인구=("총생활인구수", "mean"),
            평균주간인구=("주간인구수(09~18)", "mean"),
            평균야간인구=("야간인구수(19~08)", "mean"),
            최대생활인구=("일최대인구수", "max"),
        )
        .reset_index()
        .sort_values("평균생활인구", ascending=False)
    )

    display = gu_summary.copy()
    for col in ["평균생활인구", "평균주간인구", "평균야간인구", "최대생활인구"]:
        display[col] = display[col].round(0).astype("int64")

    assert original_shape == (77_792, 15)
    assert living["시군구명"].nunique() == 26
    assert living["기준일"].nunique() == 2_992
    assert len(gu_summary) == 25
    assert gu_summary.iloc[0]["시군구명"] == "강남구"
    assert int(gu_summary.iloc[0]["관측일수"]) == 2_992

    print("\n[미션: 자치구별 생활인구 집계]")
    print(f"생활인구 파일: {original_shape[0]:,}행, {original_shape[1]}열")
    print(f"기간: {living['기준일'].min().date()} ~ {living['기준일'].max().date()}")
    print(f"자치구 집계 결과: {len(gu_summary):,}행")
    print_table("평균생활인구 상위 10개 자치구", display, 10)

    return gu_summary


def main() -> None:
    build_shop_order_analysis()
    build_population_melt_demo()
    build_store_top10()
    solve_living_population_mission()
    print("\n검증 통과")


if __name__ == "__main__":
    main()
