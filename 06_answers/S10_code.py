from __future__ import annotations


def average(numbers: list[int]) -> float:
    total = 0
    for number in numbers:
        total = total + number
    return total / len(numbers)


def main() -> None:
    store_name = "강남점"
    today_sales = 170000
    discount_rate = 0.1
    is_weekend = False

    print("변수와 자료형")
    print(store_name, type(store_name).__name__)
    print(today_sales, type(today_sales).__name__)
    print(discount_rate, type(discount_rate).__name__)
    print(is_weekend, type(is_weekend).__name__)

    sales_list = [120000, 98000, 135000, 170000, 155000]

    total_sales = 0
    for amount in sales_list:
        total_sales = total_sales + amount

    average_sales = total_sales / len(sales_list)

    print("\n따라하기 결과")
    print(f"매출 리스트: {sales_list}")
    print(f"매출 개수: {len(sales_list)}")
    print(f"매출 합계: {total_sales}")
    print(f"매출 평균: {average_sales}")

    one_day = {
        "요일": "월",
        "매출": 120000,
    }
    print("\n딕셔너리 예시")
    print(one_day["요일"], one_day["매출"])

    daily_sales = [
        {"요일": "월", "매출": 120000},
        {"요일": "화", "매출": 98000},
        {"요일": "수", "매출": 135000},
        {"요일": "목", "매출": 170000},
        {"요일": "금", "매출": 155000},
        {"요일": "토", "매출": 210000},
        {"요일": "일", "매출": 190000},
    ]

    print("\n금요일 필터 예시")
    for row in daily_sales:
        if row["요일"] == "금":
            print(row)

    weekday_names = ["월", "화", "수", "목", "금"]
    weekday_rows = []
    weekday_total = 0

    for row in daily_sales:
        if row["요일"] in weekday_names:
            weekday_rows.append(row)
            weekday_total = weekday_total + row["매출"]

    weekday_average = weekday_total / len(weekday_rows)

    print("\n미션 결과")
    print(f"평일 행수: {len(weekday_rows)}")
    print(f"평일 매출 합계: {weekday_total}")
    print(f"평일 매출 평균: {weekday_average}")
    print(f"평일 행: {weekday_rows}")

    print("\n함수 맛보기")
    print(f"average(sales_list): {average(sales_list)}")

    assert total_sales == 678000
    assert average_sales == 135600.0
    assert len(weekday_rows) == 5
    assert weekday_total == 678000
    assert weekday_average == 135600.0
    assert average(sales_list) == 135600.0
    print("\n검증 통과")


if __name__ == "__main__":
    main()
