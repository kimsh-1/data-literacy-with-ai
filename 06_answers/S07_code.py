from pathlib import Path

import pandas as pd

data_path = Path("/mnt/d/ai-data-analysis-course/02_datasets/cafe_sales/cafe_sales_dirty.csv")
df = pd.read_csv(data_path)

expected_columns = [
    "order_id",
    "date",
    "weekday",
    "hour",
    "store",
    "category",
    "item",
    "unit_price",
    "qty",
    "amount",
    "payment",
    "member",
]

assert df.shape == (10439, 12)
assert list(df.columns) == expected_columns

date_parsed = pd.to_datetime(df["date"], format="mixed", errors="coerce")
unit_price_num = pd.to_numeric(
    df["unit_price"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("원", "", regex=False)
    .str.strip(),
    errors="coerce",
)

work = df.assign(
    date_parsed=date_parsed,
    unit_price_num=unit_price_num,
)
work["amount_mismatch"] = work["amount"] != work["unit_price_num"] * work["qty"]

date_format_counts = {
    "YYYY-MM-DD": int(df["date"].str.match(r"^\d{4}-\d{2}-\d{2}$").sum()),
    "YYYY/MM/DD": int(df["date"].str.match(r"^\d{4}/\d{2}/\d{2}$").sum()),
    "MM-DD-YYYY": int(df["date"].str.match(r"^\d{2}-\d{2}-\d{4}$").sum()),
}

quality_summary = {
    "전체 행 수": len(df),
    "전체 열 수": len(df.columns),
    "완전 중복 행": int(df.duplicated().sum()),
    "중복 order_id 추가 행": int(df["order_id"].duplicated().sum()),
    "payment 결측": int(df["payment"].isna().sum()),
    "member 결측": int(df["member"].isna().sum()),
    "store 값 '강남 점'": int((df["store"] == "강남 점").sum()),
    "앞 공백 category": int(df["category"].str.startswith(" ", na=False).sum()),
    "unit_price에 원 문자 포함": int(df["unit_price"].astype(str).str.contains("원", regex=False).sum()),
    "qty > 20": int((df["qty"] > 20).sum()),
    "amount <= 0": int((df["amount"] <= 0).sum()),
    "단가x수량과 금액 불일치": int(work["amount_mismatch"].sum()),
}

analysis = work.drop_duplicates("order_id", keep="first").copy()

anomaly_mask = (
    analysis["date_parsed"].isna()
    | (analysis["qty"] > 20)
    | (analysis["amount"] <= 0)
    | (analysis["amount_mismatch"])
)

anomalies = analysis.loc[
    anomaly_mask,
    ["order_id", "date", "item", "unit_price_num", "qty", "amount", "amount_mismatch"],
].sort_values("order_id")

cleaned = analysis.loc[~anomaly_mask].copy()
cleaned["month"] = cleaned["date_parsed"].dt.to_period("M").astype(str)

monthly = (
    cleaned.groupby("month")
    .agg(
        주문건수=("order_id", "count"),
        판매수량=("qty", "sum"),
        매출액=("amount", "sum"),
    )
    .reset_index()
)
monthly["전월대비 증감액"] = monthly["매출액"].diff().fillna(0).astype(int)
monthly["전월대비 증감률"] = monthly["매출액"].pct_change().mul(100).round(1)

daily = (
    cleaned.groupby("date_parsed")
    .agg(
        주문건수=("order_id", "count"),
        판매수량=("qty", "sum"),
        매출액=("amount", "sum"),
    )
    .reset_index()
    .rename(columns={"date_parsed": "date"})
)

q1 = daily["매출액"].quantile(0.25)
q3 = daily["매출액"].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
daily_outliers = daily[(daily["매출액"] < lower_bound) | (daily["매출액"] > upper_bound)]
top_daily = daily.sort_values("매출액", ascending=False).head(3)

assert len(cleaned) == 10421
assert int(cleaned["amount"].sum()) == 90476000
assert int(monthly.loc[monthly["month"] == "2025-06", "매출액"].iloc[0]) == 16816500
assert len(anomalies) == 3
assert len(daily_outliers) == 0

print("데이터 행열:", df.shape)
print("날짜 형식 수:", date_format_counts)
print("품질 점검:", quality_summary)
print()
print("[월별 매출 추세]")
print(monthly.to_string(index=False))
print()
print("[이상치로 제외한 행]")
print(anomalies.to_string(index=False))
print()
print("일별 매출 IQR 상한:", int(upper_bound))
print("일별 매출 이상치 수:", len(daily_outliers))
print("[일별 매출 상위 3일]")
print(top_daily.to_string(index=False))
