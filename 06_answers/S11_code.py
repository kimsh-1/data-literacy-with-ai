from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path("/mnt/d/ai-data-analysis-course")
if not ROOT.exists():
    ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "02_datasets/cafe_sales/cafe_sales_clean.csv"


def main() -> None:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

    print("1. 데이터 로드")
    print(f"pandas: {pd.__version__}")
    print(f"파일: {DATA_PATH}")
    print(f"행/열: {df.shape[0]}행 x {df.shape[1]}열")
    print("컬럼:", ", ".join(df.columns))

    print("\n2. DataFrame과 Series")
    amount_series = df["amount"]
    print(f"df의 타입: {type(df).__name__}")
    print(f"df['amount']의 타입: {type(amount_series).__name__}")
    print(f"amount Series 길이: {len(amount_series)}")

    print("\n3. head")
    print(df.head(3).to_string(index=False))

    print("\n4. info")
    df.info()

    print("\n5. describe 주요 숫자")
    print(df[["unit_price", "qty", "amount"]].describe().round(2).to_string())

    print("\n6. 강남점 불리언 필터")
    gangnam_mask = df["store"] == "강남점"
    gangnam = df.loc[gangnam_mask].copy()
    print(f"강남점 행수: {len(gangnam)}")
    print(gangnam.head(5).to_string(index=False))

    print("\n7. 강남점 금액 내림차순 정렬")
    display_cols = ["order_id", "date", "store", "category", "item", "qty", "amount"]
    gangnam_sorted = gangnam.sort_values(
        ["amount", "date", "order_id"],
        ascending=[False, True, True],
    )
    print(gangnam_sorted.loc[:, display_cols].head(5).to_string(index=False))

    print("\n8. loc와 iloc")
    print("df.loc[0, 'store']:", df.loc[0, "store"])
    print("df.iloc[0, 4]:", df.iloc[0, 4])
    print("df.loc[0:2, ['date', 'store', 'amount']]")
    print(df.loc[0:2, ["date", "store", "amount"]].to_string(index=True))
    print("df.iloc[0:3, [1, 4, 9]]")
    print(df.iloc[0:3, [1, 4, 9]].to_string(index=True))

    print("\n9. 미션: 강남점 커피 중 10,000원 이상 주문")
    mission_mask = (
        (df["store"] == "강남점")
        & (df["category"] == "커피")
        & (df["amount"] >= 10000)
    )
    mission = (
        df.loc[mission_mask, display_cols]
        .sort_values(["amount", "date", "order_id"], ascending=[False, True, True])
        .copy()
    )
    mission_count = len(mission)
    mission_total = int(mission["amount"].sum())
    mission_average = mission["amount"].mean()

    print(f"미션 행수: {mission_count}")
    print(f"미션 총금액: {mission_total}")
    print(f"미션 평균금액: {mission_average:.2f}")
    print(mission.head(10).to_string(index=False))

    assert DATA_PATH.exists()
    assert df.shape == (10424, 12)
    assert list(df.columns) == [
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
    assert type(df).__name__ == "DataFrame"
    assert type(amount_series).__name__ == "Series"
    assert len(amount_series) == 10424
    assert len(gangnam) == 6196
    assert df.loc[0, "store"] == df.iloc[0, 4] == "홍대점"
    assert mission_count == 1362
    assert mission_total == 16664500
    assert int(mission["amount"].max()) == 16500

    print("\n검증 통과")


if __name__ == "__main__":
    main()
