from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "02_datasets" / "shop_orders"


def money(value: float) -> str:
    return f"{value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.2%}"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
    customers = pd.read_csv(DATA / "customers.csv", parse_dates=["join_date"])
    products = pd.read_csv(DATA / "products.csv")
    return orders, customers, products


def build_model() -> tuple[pd.DataFrame, pd.DataFrame]:
    orders, customers, products = load_data()

    merged = (
        orders.merge(customers, on="customer_id", how="left", validate="many_to_one")
        .merge(products, on="product_id", how="left", validate="many_to_one")
    )
    merged["sales"] = merged["price"] * merged["qty"] * (1 - merged["discount_rate"])

    date_table = pd.DataFrame(
        {"Date": pd.date_range(orders["order_date"].min(), orders["order_date"].max(), freq="D")}
    )
    date_table["연도"] = date_table["Date"].dt.year
    date_table["월번호"] = date_table["Date"].dt.month
    date_table["연월"] = date_table["Date"].dt.strftime("%Y-%m")
    date_table["연월정렬"] = date_table["Date"].dt.year * 100 + date_table["Date"].dt.month

    assert orders.shape == (20_000, 6)
    assert customers.shape == (3_000, 7)
    assert products.shape == (200, 5)
    assert orders["order_id"].nunique() == 20_000
    assert orders["customer_id"].nunique() == 2_903
    assert orders["product_id"].nunique() == 200
    assert orders["order_date"].min().strftime("%Y-%m-%d") == "2024-01-01"
    assert orders["order_date"].max().strftime("%Y-%m-%d") == "2024-12-31"
    assert orders["order_date"].dt.to_period("M").nunique() == 12
    assert len(date_table) == 366
    assert merged["grade"].isna().sum() == 0
    assert merged["price"].isna().sum() == 0

    print(f"pandas: {pd.__version__}")
    print(f"orders: {len(orders):,}행, {orders.shape[1]}열")
    print(f"customers: {len(customers):,}행, {customers.shape[1]}열")
    print(f"products: {len(products):,}행, {products.shape[1]}열")
    print(
        "주문 기간: "
        f"{orders['order_date'].min().date()} ~ {orders['order_date'].max().date()}"
    )
    print(f"날짜테이블: {len(date_table):,}행")
    print(
        "조인 누락: "
        f"고객 {int(merged['grade'].isna().sum())}건, "
        f"상품 {int(merged['price'].isna().sum())}건"
    )

    return merged, date_table


def monthly_kpis(merged: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        merged.assign(연월=merged["order_date"].dt.strftime("%Y-%m"))
        .groupby("연월", as_index=False)
        .agg(
            주문건수=("order_id", "nunique"),
            판매수량=("qty", "sum"),
            총매출=("sales", "sum"),
        )
    )
    monthly["전월매출"] = monthly["총매출"].shift(1)
    monthly["전월대비증감액"] = monthly["총매출"] - monthly["전월매출"]
    monthly["전월대비성장률"] = monthly["전월대비증감액"] / monthly["전월매출"]
    return monthly


def category_kpis(merged: pd.DataFrame) -> pd.DataFrame:
    category = (
        merged.groupby("category", as_index=False)
        .agg(주문건수=("order_id", "nunique"), 판매수량=("qty", "sum"), 총매출=("sales", "sum"))
        .sort_values("총매출", ascending=False)
    )
    category["매출비중"] = category["총매출"] / category["총매출"].sum()
    return category


def grade_kpis(merged: pd.DataFrame) -> pd.DataFrame:
    grade = (
        merged.groupby("grade", as_index=False)
        .agg(고객수=("customer_id", "nunique"), 주문건수=("order_id", "nunique"), 총매출=("sales", "sum"))
        .sort_values("총매출", ascending=False)
    )
    return grade


def main() -> None:
    merged, _date_table = build_model()

    total_sales = merged["sales"].sum()
    total_orders = merged["order_id"].nunique()
    total_qty = int(merged["qty"].sum())
    avg_order_value = total_sales / total_orders

    assert abs(total_sales - 1_938_489_803.0) < 0.01
    assert total_orders == 20_000
    assert total_qty == 29_535
    assert round(avg_order_value, 2) == 96_924.49

    print(f"전체 주문건수: {total_orders:,}")
    print(f"전체 판매수량: {total_qty:,}")
    print(f"전체 매출: {money(total_sales)}")
    print(f"평균주문금액: {avg_order_value:,.2f}")

    monthly = monthly_kpis(merged)
    december = monthly.loc[monthly["연월"] == "2024-12"].iloc[0]
    november = monthly.loc[monthly["연월"] == "2024-11"].iloc[0]
    june = monthly.loc[monthly["연월"] == "2024-06"].iloc[0]

    assert money(december["총매출"]) == "225,576,457"
    assert money(december["전월매출"]) == "223,024,439"
    assert round(float(december["전월대비성장률"]), 4) == 0.0114
    assert round(float(november["전월대비성장률"]), 4) == 0.4043
    assert round(float(june["전월대비성장률"]), 4) == -0.1626
    assert pd.isna(monthly.loc[0, "전월매출"])

    print(f"2024-12 매출: {money(december['총매출'])}")
    print(f"2024-12 전월매출: {money(december['전월매출'])}")
    print(f"2024-12 전월대비 성장률: {pct(december['전월대비성장률'])}")
    print(f"전월대비 성장률 최고월: 2024-11, {pct(november['전월대비성장률'])}")
    print(f"전월대비 성장률 최저월: 2024-06, {pct(june['전월대비성장률'])}")

    category = category_kpis(merged)
    top_category = category.iloc[0]
    assert top_category["category"] == "디지털"
    assert money(top_category["총매출"]) == "673,862,749"
    assert round(float(top_category["매출비중"]), 4) == 0.3476

    print(
        "카테고리 1위: "
        f"{top_category['category']}, 매출 {money(top_category['총매출'])}, "
        f"비중 {pct(top_category['매출비중'])}"
    )

    grade = grade_kpis(merged)
    expected_grade_sales = {
        "실버": 603_583_519.0,
        "골드": 547_524_985.0,
        "브론즈": 393_948_369.0,
        "VIP": 393_432_930.0,
    }
    actual_grade_sales = dict(zip(grade["grade"], grade["총매출"], strict=True))
    for grade_name, expected_sales in expected_grade_sales.items():
        assert abs(actual_grade_sales[grade_name] - expected_sales) < 0.01

    print("등급별 매출 검증:")
    for row in grade.itertuples(index=False):
        print(f"- {row.grade}: {money(row.총매출)}")

    print("검증 통과")


if __name__ == "__main__":
    main()
