from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "02_datasets" / "cafe_sales" / "cafe_sales_clean.csv"


def main():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])

    print(f"pandas_version={pd.__version__}")
    print(f"data_path={DATA_PATH}")
    print(f"rows={len(df)}")
    print(f"columns={len(df.columns)}")
    print("column_names=" + ", ".join(df.columns))
    print(f"date_range={df['date'].min().date()} ~ {df['date'].max().date()}")
    print(f"missing_total={int(df.isna().sum().sum())}")
    print(f"total_amount={int(df['amount'].sum())}")
    print(f"average_order_amount={df['amount'].mean():.1f}")

    print("\nstore_sales")
    print(df.groupby("store")["amount"].sum().sort_values(ascending=False).to_string())

    print("\ncategory_sales")
    print(df.groupby("category")["amount"].sum().sort_values(ascending=False).to_string())

    print("\ntop_5_hours_by_amount")
    print(df.groupby("hour")["amount"].sum().sort_values(ascending=False).head(5).to_string())


if __name__ == "__main__":
    main()
