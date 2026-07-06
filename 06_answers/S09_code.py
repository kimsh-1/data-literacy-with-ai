from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "02_datasets" / "cafe_sales"
CLEAN_CSV = DATA_DIR / "cafe_sales_clean.csv"
DIRTY_CSV = DATA_DIR / "cafe_sales_dirty.csv"

EXPECTED_COLUMNS = [
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
    return f"{int(round(value)):,}원"


def load_sales(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"{path.name}에 필요한 컬럼이 없습니다: {sorted(missing)}")
    return df[EXPECTED_COLUMNS].copy()


def enrich_for_check(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["amount_num"] = pd.to_numeric(out["amount"], errors="coerce")
    out["qty_num"] = pd.to_numeric(out["qty"], errors="coerce")
    out["unit_price_num"] = pd.to_numeric(
        out["unit_price"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("원", "", regex=False),
        errors="coerce",
    )
    out["expected_amount"] = out["unit_price_num"] * out["qty_num"]
    out["date_parsed"] = pd.to_datetime(out["date"], format="mixed", errors="coerce")
    out["month"] = out["date_parsed"].dt.to_period("M").astype(str)
    out["store_norm"] = out["store"].astype(str).str.replace(" ", "", regex=False)
    out["category_norm"] = out["category"].astype(str).str.strip()
    out["item_norm"] = out["item"].replace(
        {"아메리카": "아메리카노", "Americano": "아메리카노", "아메 리카노": "아메리카노"}
    )
    return out


def pivot_amount(df: pd.DataFrame, index: str, columns: str | None = None) -> pd.DataFrame:
    if columns is None:
        result = df.pivot_table(index=index, values="amount_num", aggfunc="sum")
    else:
        result = df.pivot_table(index=index, columns=columns, values="amount_num", aggfunc="sum")
    return result.fillna(0).astype(int)


def dirty_issue_summary(dirty: pd.DataFrame) -> pd.DataFrame:
    category_spaces = dirty["category"].astype(str) != dirty["category"].astype(str).str.strip()
    issue_rows = [
        ["원본 대비 증가 행", len(dirty) - 10424],
        ["주문번호 중복 행", int(dirty["order_id"].duplicated().sum())],
        ["완전 동일 중복 행", int(dirty.duplicated().sum())],
        ["중복 주문번호 종류", int(dirty.loc[dirty["order_id"].duplicated(keep=False), "order_id"].nunique())],
        ["payment 결측", int(dirty["payment"].isna().sum())],
        ["member 결측", int(dirty["member"].isna().sum())],
        ["날짜 YYYY/MM/DD 형식", int(dirty["date"].astype(str).str.contains("/", regex=False).sum())],
        ["날짜 MM-DD-YYYY 형식", int(dirty["date"].astype(str).str.match(r"\d{2}-\d{2}-\d{4}", na=False).sum())],
        ["unit_price 문자 포함", int(dirty["unit_price"].astype(str).str.contains("원|,", regex=True, na=False).sum())],
        ["store='강남 점'", int((dirty["store"] == "강남 점").sum())],
        ["category 앞뒤 공백", int(category_spaces.sum())],
        ["아메리카노 표기 변형", int(dirty["item"].isin(["아메리카", "Americano", "아메 리카노"]).sum())],
        ["qty=999", int((dirty["qty_num"] == 999).sum())],
        ["amount 음수", int((dirty["amount_num"] < 0).sum())],
        ["단가×수량과 금액 불일치", int((dirty["expected_amount"] != dirty["amount_num"]).sum())],
    ]
    return pd.DataFrame(issue_rows, columns=["점검 항목", "확인값"])


def main() -> None:
    clean = enrich_for_check(load_sales(CLEAN_CSV))
    dirty = enrich_for_check(load_sales(DIRTY_CSV))

    clean_total = int(clean["amount_num"].sum())
    dirty_total = int(dirty["amount_num"].sum())
    clean_qty = int(clean["qty_num"].sum())
    dirty_qty = int(dirty["qty_num"].sum())

    clean_store_category = pivot_amount(clean, "store", "category")
    clean_store = pivot_amount(clean, "store")
    clean_category = pivot_amount(clean, "category")
    clean_monthly = clean.groupby("month")["amount_num"].sum().astype(int)

    dirty_store_raw = pivot_amount(dirty, "store")
    dirty_category_raw = pivot_amount(dirty, "category")
    dirty_store_norm = pivot_amount(dirty, "store_norm")
    dirty_category_norm = pivot_amount(dirty, "category_norm")
    dirty_monthly = dirty.groupby("month")["amount_num"].sum().astype(int)
    issues = dirty_issue_summary(dirty)

    assert pd.__version__ == "3.0.3"
    assert clean.shape == (10424, 21)
    assert dirty.shape == (10439, 21)
    assert clean_total == 90492500
    assert dirty_total == 90600500
    assert clean_qty == 17241
    assert dirty_qty == 19259
    assert clean["order_id"].nunique() == 10424
    assert dirty["order_id"].nunique() == 10424
    assert int(dirty["order_id"].duplicated().sum()) == 15
    assert int(dirty.duplicated().sum()) == 13
    assert int(dirty["payment"].isna().sum()) == 313
    assert int(dirty["member"].isna().sum()) == 209
    assert int(dirty["date"].astype(str).str.contains("/", regex=False).sum()) == 206
    assert int(dirty["date"].astype(str).str.match(r"\d{2}-\d{2}-\d{4}", na=False).sum()) == 104
    assert int((dirty["store"] == "강남 점").sum()) == 310
    assert int((dirty["category"].astype(str) != dirty["category"].astype(str).str.strip()).sum()) == 313
    assert int(dirty["item"].isin(["아메리카", "Americano", "아메 리카노"]).sum()) == 106
    assert int((dirty["qty_num"] == 999).sum()) == 2
    assert int((dirty["amount_num"] < 0).sum()) == 1
    assert int((dirty["expected_amount"] != dirty["amount_num"]).sum()) == 3
    assert int(clean_store.loc["강남점", "amount_num"]) == 53425000
    assert int(clean_store.loc["홍대점", "amount_num"]) == 37067500
    assert int(clean_category.loc["커피", "amount_num"]) == 45606000
    assert int(clean_category.loc["음료", "amount_num"]) == 25550000
    assert int(clean_category.loc["디저트", "amount_num"]) == 19336500
    assert int(clean_monthly.loc["2025-06"]) == 16816500
    assert int(dirty_monthly.loc["2025-06"]) == 16822000

    print("S09 검증 결과")
    print(f"pandas version: {pd.__version__}")
    print()

    print("[1] 파일과 규모")
    print(f"clean 파일: {CLEAN_CSV}")
    print(f"clean 규모: {len(clean):,}행 x {len(EXPECTED_COLUMNS)}열")
    print(f"dirty 파일: {DIRTY_CSV}")
    print(f"dirty 규모: {len(dirty):,}행 x {len(EXPECTED_COLUMNS)}열")
    print(f"기간: {clean['date_parsed'].min().date()} ~ {clean['date_parsed'].max().date()}")
    print()

    print("[2] clean 피벗 검산 기준값")
    print(f"총매출: {money(clean_total)}")
    print(f"판매수량 합계: {clean_qty:,}개")
    print("지점별 매출")
    print(clean_store.to_string())
    print("카테고리별 매출")
    print(clean_category.to_string())
    print("지점 x 카테고리 매출")
    print(clean_store_category.to_string())
    print("월별 매출")
    print(clean_monthly.to_string())
    print()

    print("[3] dirty 원본을 그대로 집계했을 때")
    print(f"총매출: {money(dirty_total)}")
    print(f"판매수량 합계: {dirty_qty:,}개")
    print(f"clean 총매출과 차이: {money(dirty_total - clean_total)}")
    print("원본 store 기준 매출")
    print(dirty_store_raw.to_string())
    print("원본 category 기준 매출")
    print(dirty_category_raw.to_string())
    print()

    print("[4] dirty 표기 정리 후 같은 집계")
    print("공백을 정리한 store 기준 매출")
    print(dirty_store_norm.to_string())
    print("공백을 정리한 category 기준 매출")
    print(dirty_category_norm.to_string())
    print()

    print("[5] dirty 검증 체크 항목")
    print(issues.to_string(index=False))
    print()
    print("검증 통과")


if __name__ == "__main__":
    main()
