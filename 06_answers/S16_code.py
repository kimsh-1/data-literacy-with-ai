from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "02_datasets" / "shop_orders"


def print_table(title: str, df: pd.DataFrame, max_rows: int | None = None) -> None:
    print(f"\n[{title}]")
    if max_rows is not None:
        df = df.head(max_rows)
    print(df.to_string(index=False))


def load_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
    customers = pd.read_csv(DATA / "customers.csv", parse_dates=["join_date"])
    products = pd.read_csv(DATA / "products.csv")

    assert orders.shape == (20_000, 6)
    assert customers.shape == (3_000, 7)
    assert products.shape == (200, 5)

    print("[데이터 행수 확인]")
    print(f"orders: {len(orders):,}행, {orders.shape[1]}열")
    print(f"customers: {len(customers):,}행, {customers.shape[1]}열")
    print(f"products: {len(products):,}행, {products.shape[1]}열")

    return orders, customers, products


def validate_relationships(
    orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame
) -> None:
    assert orders["order_id"].is_unique
    assert customers["customer_id"].is_unique
    assert products["product_id"].is_unique

    missing_customers = int((~orders["customer_id"].isin(customers["customer_id"])).sum())
    missing_products = int((~orders["product_id"].isin(products["product_id"])).sum())

    assert missing_customers == 0
    assert missing_products == 0

    print("\n[관계 조건 확인]")
    print("orders[order_id] 고유값:", orders["order_id"].nunique())
    print("customers[customer_id] 고유값:", customers["customer_id"].nunique())
    print("products[product_id] 고유값:", products["product_id"].nunique())
    print("orders -> customers 참조 누락:", missing_customers)
    print("orders -> products 참조 누락:", missing_products)
    print("권장 관계: customers/product/date는 1, orders는 다")


def build_date_table(orders: pd.DataFrame) -> pd.DataFrame:
    date_table = pd.DataFrame(
        {"Date": pd.date_range(orders["order_date"].min(), orders["order_date"].max(), freq="D")}
    )
    date_table["Year"] = date_table["Date"].dt.year
    date_table["MonthNo"] = date_table["Date"].dt.month
    date_table["Month"] = date_table["Date"].dt.strftime("%Y-%m")
    date_table["YearMonth"] = date_table["Date"].dt.year * 100 + date_table["Date"].dt.month
    date_table["Quarter"] = "Q" + date_table["Date"].dt.quarter.astype(str)
    date_table["Day"] = date_table["Date"].dt.day
    date_table["WeekdayNo"] = date_table["Date"].dt.weekday + 1
    date_table["Weekday"] = date_table["WeekdayNo"].map(
        {1: "월", 2: "화", 3: "수", 4: "목", 5: "금", 6: "토", 7: "일"}
    )

    assert len(date_table) == 366
    assert date_table["Date"].is_unique
    assert date_table["Date"].isna().sum() == 0
    assert date_table["Date"].min().date().isoformat() == "2024-01-01"
    assert date_table["Date"].max().date().isoformat() == "2024-12-31"

    print("\n[날짜 차원 확인]")
    print(f"주문일 범위: {orders['order_date'].min().date()} ~ {orders['order_date'].max().date()}")
    print(f"Date 테이블: {len(date_table):,}행")
    print_table("Date 테이블 앞 3행", date_table, 3)
    print("\n[Date 테이블 뒤 3행]")
    print(date_table.tail(3).to_string(index=False))

    return date_table


def calculate_sales_summary(
    orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    model_check = (
        orders.merge(products[["product_id", "category", "price"]], on="product_id", how="left")
        .merge(customers[["customer_id", "region", "grade"]], on="customer_id", how="left")
    )
    assert len(model_check) == len(orders)
    assert int(model_check[["price", "region", "grade"]].isna().sum().sum()) == 0

    model_check["sales"] = (
        model_check["price"] * model_check["qty"] * (1 - model_check["discount_rate"])
    )

    total_sales = model_check["sales"].sum()
    assert abs(total_sales - 1_938_489_803.0) < 0.1

    region_summary = (
        model_check.groupby("region", as_index=False)
        .agg(
            order_count=("order_id", "count"),
            customer_count=("customer_id", "nunique"),
            total_sales=("sales", "sum"),
            avg_order_value=("sales", "mean"),
        )
        .sort_values("total_sales", ascending=False)
    )

    assert len(region_summary) == 17
    assert int(region_summary["order_count"].sum()) == 20_000
    assert abs(region_summary["total_sales"].sum() - total_sales) < 0.1
    assert int(region_summary.iloc[0]["total_sales"]) == 570_482_124
    assert region_summary.iloc[0]["region"] == "서울특별시"

    monthly_summary = (
        model_check.assign(month=model_check["order_date"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)
        .agg(order_count=("order_id", "count"), total_sales=("sales", "sum"))
    )

    print("\n[매출 검산]")
    print(f"전체 주문 건수: {len(model_check):,}")
    print(f"전체 매출: {total_sales:,.0f}")
    print(f"지역 수: {len(region_summary):,}")
    print_table("지역별 매출 상위 10개", format_region_summary(region_summary), 10)
    print_table("월별 주문과 매출", format_monthly_summary(monthly_summary))

    return region_summary, monthly_summary


def format_region_summary(region_summary: pd.DataFrame) -> pd.DataFrame:
    display = region_summary.copy()
    display["total_sales"] = display["total_sales"].round(0).astype("int64")
    display["avg_order_value"] = display["avg_order_value"].round(2)
    return display


def format_monthly_summary(monthly_summary: pd.DataFrame) -> pd.DataFrame:
    display = monthly_summary.copy()
    display["total_sales"] = display["total_sales"].round(0).astype("int64")
    return display


def main() -> None:
    orders, customers, products = load_tables()
    validate_relationships(orders, customers, products)
    build_date_table(orders)
    calculate_sales_summary(orders, customers, products)
    print("\nS16 검증 통과")


if __name__ == "__main__":
    main()
