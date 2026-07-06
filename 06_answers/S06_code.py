from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
APT_PATH = ROOT / "02_datasets/real_korean/realestate_apt/molit_apt_sale_seoul_gangnam_2024.csv"
HR_PATH = ROOT / "02_datasets/hr_employees/hr_employees_clean.csv"
DELIVERY_PATH = ROOT / "02_datasets/real_korean/delivery_food/food_delivery_prediction_raw_data2.csv"


def format_won(value: float) -> str:
    return f"{value:,.0f}원"


def load_apartment() -> tuple[pd.DataFrame, float]:
    apt = pd.read_csv(APT_PATH)
    required = {"전용면적(㎡)", "거래금액(만원)"}
    missing = required - set(apt.columns)
    if missing:
        raise ValueError(f"아파트 데이터에 필요한 컬럼이 없습니다: {sorted(missing)}")

    apt["거래금액_만원"] = pd.to_numeric(
        apt["거래금액(만원)"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )
    usable = apt.dropna(subset=["전용면적(㎡)", "거래금액_만원"]).copy()
    corr = usable["전용면적(㎡)"].corr(usable["거래금액_만원"])
    return usable, corr


def load_hr() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    hr = pd.read_csv(HR_PATH)
    required = {"dept", "gender", "salary"}
    missing = required - set(hr.columns)
    if missing:
        raise ValueError(f"HR 데이터에 필요한 컬럼이 없습니다: {sorted(missing)}")

    overall = hr.groupby("gender")["salary"].mean().reindex(["남성", "여성"])
    by_dept = hr.pivot_table(index="dept", columns="gender", values="salary", aggfunc="mean")
    by_dept = by_dept[["남성", "여성"]].copy()
    by_dept["여성-남성"] = by_dept["여성"] - by_dept["남성"]
    return hr, overall, by_dept.sort_index()


def load_delivery_reference() -> tuple[pd.DataFrame, float]:
    delivery = pd.read_csv(DELIVERY_PATH)
    required = {"평균기온(°C)", "통화건수"}
    missing = required - set(delivery.columns)
    if missing:
        raise ValueError(f"배달 참고 데이터에 필요한 컬럼이 없습니다: {sorted(missing)}")

    corr = delivery["평균기온(°C)"].corr(delivery["통화건수"])
    return delivery, corr


def main() -> None:
    apt, apt_corr = load_apartment()
    hr, hr_overall, hr_by_dept = load_hr()
    delivery, delivery_corr = load_delivery_reference()

    male_minus_female = hr_overall["남성"] - hr_overall["여성"]
    all_dept_reversed = bool((hr_by_dept["여성"] > hr_by_dept["남성"]).all())

    print("S06 검증 결과")
    print(f"pandas version: {pd.__version__}")
    print()

    print("[1] 강남구 아파트 실거래")
    print(f"파일: {APT_PATH}")
    print(f"행수: {len(apt):,}행")
    print(f"전용면적-거래금액 Pearson 상관계수 r: {apt_corr:.3f}")
    print(
        "전용면적 범위: "
        f"{apt['전용면적(㎡)'].min():.1f}㎡ ~ {apt['전용면적(㎡)'].max():.2f}㎡"
    )
    print(
        "거래금액 범위: "
        f"{apt['거래금액_만원'].min():,.0f}만원 ~ {apt['거래금액_만원'].max():,.0f}만원"
    )
    print()

    print("[2] HR 심슨의 역설")
    print(f"파일: {HR_PATH}")
    print(f"행수: {len(hr):,}행")
    print(
        "전체 평균 연봉: "
        f"남성 {format_won(hr_overall['남성'])}, "
        f"여성 {format_won(hr_overall['여성'])}, "
        f"남성-여성 {format_won(male_minus_female)}"
    )
    print(f"부서별 평균은 5개 부서 모두 여성 > 남성인가: {all_dept_reversed}")
    print("부서별 평균 연봉")
    print(hr_by_dept.round(0).astype(int).to_string())
    print()

    print("[3] 상관이 없을 수도 있다는 참고 반례")
    print(f"파일: {DELIVERY_PATH}")
    print(f"행수: {len(delivery):,}행")
    print(f"평균기온-통화건수 Pearson 상관계수 r: {delivery_corr:.3f}")


if __name__ == "__main__":
    main()
