from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "02_datasets" / "cafe_sales"

CLEAN_CSV = DATA_DIR / "cafe_sales_clean.csv"
DIRTY_CSV = DATA_DIR / "cafe_sales_dirty.csv"
CLEAN_XLSX = DATA_DIR / "cafe_sales_clean.xlsx"
DIRTY_XLSX = DATA_DIR / "cafe_sales_dirty.xlsx"

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


def main() -> None:
    clean = pd.read_csv(CLEAN_CSV)
    dirty = pd.read_csv(DIRTY_CSV)
    clean_xlsx = pd.read_excel(CLEAN_XLSX, sheet_name="sales")
    dirty_xlsx = pd.read_excel(DIRTY_XLSX, sheet_name="sales")

    print("파일 존재 확인")
    for path in [CLEAN_CSV, DIRTY_CSV, CLEAN_XLSX, DIRTY_XLSX]:
        print(f"- {path}: {path.exists()}")

    print("\n행수와 열수")
    print(f"clean csv: {clean.shape}")
    print(f"dirty csv: {dirty.shape}")
    print(f"clean xlsx: {clean_xlsx.shape}")
    print(f"dirty xlsx: {dirty_xlsx.shape}")

    print("\n컬럼")
    print(list(clean.columns))

    unit_price_text = dirty["unit_price"].astype(str).str.contains("원|,", regex=True, na=False)
    slash_dates = dirty["date"].astype(str).str.contains("/", regex=False, na=False)
    mdy_dash_dates = dirty["date"].astype(str).str.match(r"\d{2}-\d{2}-\d{4}", na=False)
    category_spaces = dirty["category"].astype(str) != dirty["category"].astype(str).str.strip()
    qty_numeric = pd.to_numeric(dirty["qty"], errors="coerce")
    amount_numeric = pd.to_numeric(dirty["amount"], errors="coerce")
    unit_price_numeric = pd.to_numeric(
        dirty["unit_price"].astype(str).str.replace(",", "", regex=False).str.replace("원", "", regex=False),
        errors="coerce",
    )

    issue_summary = pd.DataFrame(
        [
            ["원본 대비 증가 행", len(dirty) - len(clean)],
            ["주문번호 중복", dirty["order_id"].duplicated().sum()],
            ["완전 동일 중복 행", dirty.duplicated().sum()],
            ["payment 결측", dirty["payment"].isna().sum()],
            ["member 결측", dirty["member"].isna().sum()],
            ["날짜 YYYY/MM/DD 형식", slash_dates.sum()],
            ["날짜 MM-DD-YYYY 형식", mdy_dash_dates.sum()],
            ["unit_price 문자 포함", unit_price_text.sum()],
            ["store='강남 점'", (dirty["store"] == "강남 점").sum()],
            ["category 앞뒤 공백", category_spaces.sum()],
            ["item='아메리카'", (dirty["item"] == "아메리카").sum()],
            ["item='Americano'", (dirty["item"] == "Americano").sum()],
            ["item='아메 리카노'", (dirty["item"] == "아메 리카노").sum()],
            ["qty=999", (qty_numeric == 999).sum()],
            ["amount 음수", (amount_numeric < 0).sum()],
            ["단가×수량과 금액 불일치", ((unit_price_numeric * qty_numeric) != amount_numeric).sum()],
        ],
        columns=["항목", "확인값"],
    )

    scale_table = pd.DataFrame(
        [
            ["order_id", "식별자", "중복 확인, 주문 추적"],
            ["date", "날짜형", "일별, 월별, 요일별 추세"],
            ["weekday", "순서가 있는 범주형", "요일별 집계, 주중·주말 비교"],
            ["hour", "시간형 수치", "시간대별 주문 수"],
            ["store", "범주형", "지점별 비교"],
            ["category", "범주형", "상품 대분류별 비교"],
            ["item", "범주형", "상품별 비교"],
            ["unit_price", "수치형", "단가 계산"],
            ["qty", "수치형", "수량 합계와 평균"],
            ["amount", "수치형", "총매출과 평균 주문금액"],
            ["payment", "범주형", "결제수단별 비중"],
            ["member", "논리형", "회원 여부별 비교"],
        ],
        columns=["컬럼", "척도", "가능한 분석"],
    )

    print("\ndirty 문제 요약")
    print(issue_summary.to_string(index=False))

    print("\n척도 분류표")
    print(scale_table.to_string(index=False))

    assert clean.shape == (10424, 12)
    assert dirty.shape == (10439, 12)
    assert clean_xlsx.shape == (10424, 12)
    assert dirty_xlsx.shape == (10439, 12)
    assert list(clean.columns) == EXPECTED_COLUMNS
    assert list(dirty.columns) == EXPECTED_COLUMNS
    assert len(dirty) - len(clean) == 15
    assert dirty["order_id"].duplicated().sum() == 15
    assert dirty.duplicated().sum() == 13
    assert dirty["payment"].isna().sum() == 313
    assert dirty["member"].isna().sum() == 209
    assert slash_dates.sum() == 206
    assert mdy_dash_dates.sum() == 104
    assert unit_price_text.sum() == 157
    assert (dirty["store"] == "강남 점").sum() == 310
    assert category_spaces.sum() == 313
    assert (dirty["item"] == "아메리카").sum() == 37
    assert (dirty["item"] == "Americano").sum() == 36
    assert (dirty["item"] == "아메 리카노").sum() == 33
    assert (qty_numeric == 999).sum() == 2
    assert (amount_numeric < 0).sum() == 1
    assert ((unit_price_numeric * qty_numeric) != amount_numeric).sum() == 3

    print("\n검증 통과")


if __name__ == "__main__":
    main()
