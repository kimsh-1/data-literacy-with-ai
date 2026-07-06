from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CAFE_DIRTY = ROOT / "02_datasets/cafe_sales/cafe_sales_dirty.csv"
CP949_ORIGINAL = (
    ROOT
    / "02_datasets/real_korean/delivery_food/food_delivery_prediction_raw_data2_ORIGINAL_cp949.csv"
)

EXPECTED_CAFE_COLUMNS = [
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


def money(value: float) -> str:
    return f"{value:,.0f}원"


def load_cafe_dirty() -> pd.DataFrame:
    df = pd.read_csv(CAFE_DIRTY, encoding="utf-8-sig")
    missing = set(EXPECTED_CAFE_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"cafe_sales_dirty.csv에 필요한 컬럼이 없습니다: {sorted(missing)}")
    return df[EXPECTED_CAFE_COLUMNS].copy()


def issue_summary(raw: pd.DataFrame) -> pd.DataFrame:
    unit_price_num = pd.to_numeric(
        raw["unit_price"]
        .astype("string")
        .str.replace(",", "", regex=False)
        .str.replace("원", "", regex=False),
        errors="coerce",
    )
    qty_num = pd.to_numeric(raw["qty"], errors="coerce")
    amount_num = pd.to_numeric(raw["amount"], errors="coerce")
    date_parsed = pd.to_datetime(raw["date"], format="mixed", errors="coerce")
    expected_amount = unit_price_num * qty_num

    rows = [
        ["전체 행수", len(raw)],
        ["고유 order_id", raw["order_id"].nunique()],
        ["중복 order_id 행", int(raw.duplicated("order_id").sum())],
        ["완전 동일 중복 행", int(raw.duplicated().sum())],
        ["payment 결측", int(raw["payment"].isna().sum())],
        ["member 결측", int(raw["member"].isna().sum())],
        ["날짜 YYYY/MM/DD 형식", int(raw["date"].astype("string").str.contains("/", regex=False).sum())],
        [
            "날짜 MM-DD-YYYY 형식",
            int(raw["date"].astype("string").str.match(r"\d{2}-\d{2}-\d{4}", na=False).sum()),
        ],
        ["날짜 변환 실패", int(date_parsed.isna().sum())],
        [
            "unit_price 문자 포함",
            int(raw["unit_price"].astype("string").str.contains("원|,", regex=True, na=False).sum()),
        ],
        ["unit_price 숫자 변환 실패", int(unit_price_num.isna().sum())],
        ["store='강남 점'", int((raw["store"] == "강남 점").sum())],
        [
            "category 앞뒤 공백",
            int((raw["category"].astype("string") != raw["category"].astype("string").str.strip()).sum()),
        ],
        [
            "아메리카노 표기 변형",
            int(raw["item"].isin(["아메리카", "Americano", "아메 리카노"]).sum()),
        ],
        ["qty=999", int((qty_num == 999).sum())],
        ["amount 음수", int((amount_num < 0).sum())],
        ["단가 x 수량과 금액 불일치", int((expected_amount != amount_num).sum())],
    ]
    return pd.DataFrame(rows, columns=["점검 항목", "확인값"])


def clean_cafe_sales(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int | float]]:
    cleaned = raw.copy()

    cleaned["store"] = cleaned["store"].astype("string").str.strip().str.replace(" ", "", regex=False)
    cleaned["category"] = cleaned["category"].astype("string").str.strip()
    cleaned["item"] = (
        cleaned["item"]
        .astype("string")
        .str.strip()
        .replace(
            {
                "아메리카": "아메리카노",
                "Americano": "아메리카노",
                "아메 리카노": "아메리카노",
            }
        )
    )
    cleaned["payment"] = cleaned["payment"].astype("string").str.strip().fillna("미확인")
    cleaned["member"] = cleaned["member"].astype("boolean").fillna(False)
    cleaned["unit_price"] = pd.to_numeric(
        cleaned["unit_price"]
        .astype("string")
        .str.replace(",", "", regex=False)
        .str.replace("원", "", regex=False),
        errors="coerce",
    )
    cleaned["qty"] = pd.to_numeric(cleaned["qty"], errors="coerce")
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
    cleaned["date"] = pd.to_datetime(cleaned["date"], format="mixed", errors="coerce")

    before_drop_duplicate = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["order_id"], keep="first").copy()
    duplicate_removed = before_drop_duplicate - len(cleaned)

    before_dropna = len(cleaned)
    cleaned = cleaned.dropna(
        subset=["date", "store", "category", "item", "unit_price", "qty", "amount"]
    ).copy()
    missing_removed = before_dropna - len(cleaned)

    q1 = cleaned["qty"].quantile(0.25)
    q3 = cleaned["qty"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    qty_outlier_mask = ~cleaned["qty"].between(lower, upper)
    qty_outliers_removed = int(qty_outlier_mask.sum())
    cleaned = cleaned.loc[~qty_outlier_mask].copy()

    nonpositive_amount_mask = cleaned["amount"] <= 0
    nonpositive_amount_removed = int(nonpositive_amount_mask.sum())
    cleaned = cleaned.loc[~nonpositive_amount_mask].copy()

    for col in ["order_id", "hour", "unit_price", "qty", "amount"]:
        cleaned[col] = cleaned[col].astype("int64")

    cleaned["expected_amount"] = cleaned["unit_price"] * cleaned["qty"]
    cleaned["date_month"] = cleaned["date"].dt.to_period("M").astype("string")

    log = {
        "duplicates_removed": duplicate_removed,
        "missing_removed": missing_removed,
        "qty_q1": q1,
        "qty_q3": q3,
        "qty_iqr": iqr,
        "qty_lower": lower,
        "qty_upper": upper,
        "qty_outliers_removed": qty_outliers_removed,
        "nonpositive_amount_removed": nonpositive_amount_removed,
    }
    return cleaned, log


def compare_before_after(raw: pd.DataFrame, cleaned: pd.DataFrame) -> pd.DataFrame:
    raw_qty = pd.to_numeric(raw["qty"], errors="coerce")
    raw_amount = pd.to_numeric(raw["amount"], errors="coerce")
    rows = [
        ["행수", f"{len(raw):,}", f"{len(cleaned):,}"],
        ["고유 order_id", f"{raw['order_id'].nunique():,}", f"{cleaned['order_id'].nunique():,}"],
        ["총매출", money(raw_amount.sum()), money(cleaned["amount"].sum())],
        ["판매수량 합계", f"{raw_qty.sum():,.0f}", f"{cleaned['qty'].sum():,.0f}"],
        ["건당 평균금액", money(raw_amount.mean()), money(cleaned["amount"].mean())],
        ["건당 중앙값", money(raw_amount.median()), money(cleaned["amount"].median())],
        ["최대 수량", f"{raw_qty.max():,.0f}", f"{cleaned['qty'].max():,.0f}"],
        ["최소 금액", money(raw_amount.min()), money(cleaned["amount"].min())],
    ]
    return pd.DataFrame(rows, columns=["비교 항목", "청소 전", "청소 후"])


def load_cp949_original() -> tuple[pd.DataFrame, str]:
    try:
        pd.read_csv(CP949_ORIGINAL)
        default_read_result = "기본 UTF-8 읽기 성공"
    except UnicodeDecodeError as exc:
        default_read_result = f"기본 UTF-8 읽기 실패: {type(exc).__name__}"

    df = pd.read_csv(CP949_ORIGINAL, encoding="cp949")
    df["일자_dt"] = pd.to_datetime(df["일자"], errors="coerce")
    return df, default_read_result


def main() -> None:
    raw = load_cafe_dirty()
    issues = issue_summary(raw)
    cleaned, log = clean_cafe_sales(raw)
    comparison = compare_before_after(raw, cleaned)
    cp949_df, default_read_result = load_cp949_original()

    assert raw.shape == (10439, 12)
    assert cleaned.shape[0] == 10421
    assert raw["order_id"].nunique() == 10424
    assert cleaned["order_id"].nunique() == 10421
    assert log["duplicates_removed"] == 15
    assert log["missing_removed"] == 0
    assert log["qty_outliers_removed"] == 2
    assert log["nonpositive_amount_removed"] == 1
    assert int(cleaned.duplicated("order_id").sum()) == 0
    assert int((cleaned["expected_amount"] != cleaned["amount"]).sum()) == 0
    assert int(cleaned.isna().sum().sum()) == 0
    assert int(cleaned["qty"].max()) == 3
    assert int(cleaned["amount"].min()) == 3000
    assert cp949_df.shape == (1947, 16)
    assert int(cp949_df["일자_dt"].isna().sum()) == 0

    print("S12 검증 결과")
    print(f"pandas version: {pd.__version__}")
    print()

    print("[1] cafe_sales_dirty 점검")
    print(f"파일: {CAFE_DIRTY}")
    print(f"원본 규모: {len(raw):,}행 x {raw.shape[1]}열")
    print(issues.to_string(index=False))
    print()

    print("[2] 정제 로그")
    print(f"중복 order_id 제거: {log['duplicates_removed']}행")
    print(f"필수값 결측으로 제거: {log['missing_removed']}행")
    print(
        "qty IQR 기준: "
        f"Q1={log['qty_q1']:.1f}, Q3={log['qty_q3']:.1f}, "
        f"IQR={log['qty_iqr']:.1f}, 정상범위 {log['qty_lower']:.1f}~{log['qty_upper']:.1f}"
    )
    print(f"qty IQR 이상치 제거: {log['qty_outliers_removed']}행")
    print(f"amount 0 이하 제거: {log['nonpositive_amount_removed']}행")
    print(f"정제 후 규모: {len(cleaned):,}행 x {cleaned.shape[1]}열")
    print()

    print("[3] 청소 전후 비교")
    print(comparison.to_string(index=False))
    print()

    print("[4] 정제 후 검산")
    print(f"중복 order_id: {int(cleaned.duplicated('order_id').sum())}")
    print(f"전체 결측값: {int(cleaned.isna().sum().sum())}")
    print(f"단가 x 수량과 금액 불일치: {int((cleaned['expected_amount'] != cleaned['amount']).sum())}")
    print("카테고리별 정제 후 매출")
    category_summary = (
        cleaned.groupby("category")
        .agg(행수=("order_id", "count"), 총매출=("amount", "sum"), 판매수량=("qty", "sum"))
        .sort_index()
    )
    print(category_summary.to_string())
    print()

    print("[5] cp949 원본 인코딩과 날짜 파싱")
    print(f"파일: {CP949_ORIGINAL}")
    print(default_read_result)
    print(f"encoding='cp949' 재로드 규모: {len(cp949_df):,}행 x {cp949_df.shape[1] - 1}열")
    print(
        "일자_dt 변환 실패: "
        f"{int(cp949_df['일자_dt'].isna().sum())}건, "
        f"기간 {cp949_df['일자_dt'].min().date()} ~ {cp949_df['일자_dt'].max().date()}"
    )
    print()
    print("검증 통과")


if __name__ == "__main__":
    main()
