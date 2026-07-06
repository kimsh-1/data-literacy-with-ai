# -*- coding: utf-8 -*-
"""
shop_orders 데이터 생성기 (한국형 쇼핑몰 관계형 clean 데이터)
- clean: BI-ready 3테이블 스타스키마 실습용 (csv + 3시트 xlsx)
- dirty: 생성하지 않음
실행: python gen_shop_orders.py
산출: ../shop_orders/clean/orders.csv, customers.csv, products.csv, shop_orders_clean.xlsx
"""
import os

import numpy as np
import pandas as pd


SEED = 42
rng = np.random.default_rng(SEED)

OUT = os.path.join(os.path.dirname(__file__), "..", "shop_orders", "clean")
os.makedirs(OUT, exist_ok=True)

N_CUSTOMERS = 3_000
N_PRODUCTS = 200
N_ORDERS = 20_000


# ---- 고객 마스터 ----
REGIONS = [
    "서울특별시", "경기도", "부산광역시", "인천광역시", "대구광역시", "대전광역시",
    "광주광역시", "울산광역시", "세종특별자치시", "강원특별자치도", "충청북도", "충청남도",
    "전북특별자치도", "전라남도", "경상북도", "경상남도", "제주특별자치도",
]
REGION_WEIGHTS = np.array([
    0.195, 0.245, 0.065, 0.060, 0.050, 0.040,
    0.035, 0.030, 0.015, 0.030, 0.035, 0.045,
    0.035, 0.035, 0.050, 0.055, 0.025,
])
REGION_WEIGHTS = REGION_WEIGHTS / REGION_WEIGHTS.sum()

REGION_ORDER_MULT = {
    "서울특별시": 1.34,
    "경기도": 1.22,
    "부산광역시": 1.08,
    "인천광역시": 1.02,
    "대구광역시": 0.98,
    "대전광역시": 0.96,
    "광주광역시": 0.92,
    "울산광역시": 0.90,
    "세종특별자치시": 1.05,
    "강원특별자치도": 0.82,
    "충청북도": 0.84,
    "충청남도": 0.88,
    "전북특별자치도": 0.80,
    "전라남도": 0.78,
    "경상북도": 0.86,
    "경상남도": 0.91,
    "제주특별자치도": 1.03,
}

SURNAMES = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "류", "홍", "전", "고", "문", "양", "손", "배", "백", "허", "유", "남", "심", "노", "하", "곽", "성", "차", "주", "우", "구", "민"]
SURNAME_WEIGHTS = np.array([21, 15, 8, 5, 5, 3, 3, 3, 2.8, 2.6, 2.2, 2.1, 2.0, 1.9, 1.8, 1.7, 1.6, 1.5, 1.3, 1.3, 1.2, 1.1, 1.1, 1.0, 1.0, 0.9, 0.8, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6, 0.5, 0.5, 0.5, 0.5, 0.4, 0.4, 0.3])
SURNAME_WEIGHTS = SURNAME_WEIGHTS / SURNAME_WEIGHTS.sum()
GIVEN_SYLLABLES = ["민", "서", "지", "현", "준", "윤", "하", "도", "수", "아", "은", "우", "연", "영", "진", "성", "호", "예", "원", "재", "유", "빈", "채", "시", "태", "건", "소", "나", "다", "린", "율", "희"]


def make_korean_name() -> str:
    surname = str(rng.choice(SURNAMES, p=SURNAME_WEIGHTS))
    first = str(rng.choice(GIVEN_SYLLABLES))
    second = str(rng.choice(GIVEN_SYLLABLES))
    if first == second and rng.random() < 0.65:
        second = str(rng.choice(GIVEN_SYLLABLES))
    return surname + first + second


def random_dates(start: str, end: str, n: int) -> pd.DatetimeIndex:
    dates = pd.date_range(start, end, freq="D")
    picked = rng.integers(0, len(dates), size=n)
    return dates[picked]


customer_ids = [f"C{i:06d}" for i in range(1, N_CUSTOMERS + 1)]
customer_regions = rng.choice(REGIONS, size=N_CUSTOMERS, p=REGION_WEIGHTS)
genders = rng.choice(["남", "여"], size=N_CUSTOMERS, p=[0.48, 0.52])

age_buckets = rng.choice(
    ["10대", "20대", "30대", "40대", "50대", "60대"],
    size=N_CUSTOMERS,
    p=[0.06, 0.24, 0.27, 0.23, 0.15, 0.05],
)
age_ranges = {
    "10대": (18, 19),
    "20대": (20, 29),
    "30대": (30, 39),
    "40대": (40, 49),
    "50대": (50, 59),
    "60대": (60, 69),
}
ages = np.array([rng.integers(age_ranges[b][0], age_ranges[b][1] + 1) for b in age_buckets])

join_dates = random_dates("2019-01-01", "2024-11-30", N_CUSTOMERS)
tenure_days = (pd.Timestamp("2024-12-31") - join_dates).days

region_grade_bonus = np.array([
    0.42 if r == "서울특별시" else
    0.25 if r == "경기도" else
    0.18 if r in ["부산광역시", "세종특별자치시"] else
    0.08 if r in ["인천광역시", "제주특별자치도"] else
    0.0
    for r in customer_regions
])
age_grade_bonus = np.where((ages >= 30) & (ages <= 49), 0.20, np.where(ages >= 50, 0.08, -0.10))
tenure_bonus = (tenure_days / tenure_days.max()) * 0.45
grade_score = rng.normal(0, 0.55, size=N_CUSTOMERS) + region_grade_bonus + age_grade_bonus + tenure_bonus
t1, t2, t3 = np.quantile(grade_score, [0.40, 0.75, 0.93])
grades = np.select(
    [grade_score < t1, grade_score < t2, grade_score < t3],
    ["브론즈", "실버", "골드"],
    default="VIP",
)

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "name": [make_korean_name() for _ in range(N_CUSTOMERS)],
    "gender": genders,
    "age": ages,
    "region": customer_regions,
    "join_date": join_dates.strftime("%Y-%m-%d"),
    "grade": grades,
})


# ---- 상품 마스터 ----
CATEGORY_CONFIG = {
    "패션": {
        "n": 32, "price": (12_900, 159_000), "cost_ratio": (0.44, 0.64), "demand": 1.18,
        "mods": ["베이직", "프리미엄", "오버핏", "데일리", "시그니처", "라이트", "시즌", "모던"],
        "items": ["티셔츠", "니트", "셔츠", "슬랙스", "원피스", "자켓", "후드", "스커트"],
        "opts": ["블랙", "아이보리", "네이비", "차콜", "크림"],
    },
    "뷰티": {
        "n": 28, "price": (7_900, 89_000), "cost_ratio": (0.34, 0.56), "demand": 1.16,
        "mods": ["수분", "저자극", "글로우", "비건", "더마", "프리미엄", "데일리", "올인원"],
        "items": ["토너", "세럼", "크림", "선크림", "클렌저", "마스크팩", "립밤", "쿠션"],
        "opts": ["기획세트", "대용량", "휴대용", "리필", "무향"],
    },
    "식품": {
        "n": 28, "price": (3_900, 69_000), "cost_ratio": (0.55, 0.76), "demand": 1.22,
        "mods": ["국산", "간편", "저당", "프리미엄", "산지직송", "유기농", "든든한", "실속"],
        "items": ["현미밥", "김치", "닭가슴살", "견과", "두유", "즉석국", "샐러드", "과일청"],
        "opts": ["10팩", "대용량", "혼합세트", "정기배송", "선물세트"],
    },
    "생활용품": {
        "n": 25, "price": (5_900, 129_000), "cost_ratio": (0.46, 0.68), "demand": 0.94,
        "mods": ["항균", "모던", "리필형", "대용량", "친환경", "프리미엄", "심플", "올인원"],
        "items": ["세제", "수건", "보관함", "멀티탭", "방향제", "주방매트", "청소포", "정리함"],
        "opts": ["2입", "4입", "화이트", "그레이", "패밀리팩"],
    },
    "디지털": {
        "n": 24, "price": (19_900, 799_000), "cost_ratio": (0.66, 0.86), "demand": 0.66,
        "mods": ["무선", "고속", "스마트", "프로", "컴팩트", "게이밍", "라이트", "프리미엄"],
        "items": ["이어폰", "충전기", "키보드", "마우스", "태블릿", "스피커", "공기청정기", "모니터"],
        "opts": ["블랙", "화이트", "미니", "패키지", "신형"],
    },
    "스포츠": {
        "n": 22, "price": (9_900, 189_000), "cost_ratio": (0.45, 0.67), "demand": 0.78,
        "mods": ["러닝", "요가", "홈트", "아웃도어", "쿨링", "프로", "경량", "방수"],
        "items": ["레깅스", "운동화", "덤벨", "매트", "물병", "바람막이", "양말", "보호대"],
        "opts": ["블랙", "네이비", "세트", "라이트", "프리미엄"],
    },
    "반려동물": {
        "n": 17, "price": (4_900, 119_000), "cost_ratio": (0.50, 0.72), "demand": 0.58,
        "mods": ["저알러지", "튼튼한", "프리미엄", "소프트", "대용량", "휴대용", "위생", "데일리"],
        "items": ["사료", "간식", "배변패드", "하네스", "장난감", "샴푸", "방석", "급수기"],
        "opts": ["강아지", "고양이", "소형", "중형", "대형"],
    },
    "유아동": {
        "n": 14, "price": (6_900, 149_000), "cost_ratio": (0.47, 0.69), "demand": 0.55,
        "mods": ["무형광", "안심", "키즈", "베이비", "부드러운", "튼튼한", "교육용", "프리미엄"],
        "items": ["내의", "물티슈", "보습크림", "장난감", "책가방", "식판", "블록", "이불"],
        "opts": ["핑크", "블루", "세트", "리필", "선물세트"],
    },
    "문구/오피스": {
        "n": 10, "price": (2_900, 79_000), "cost_ratio": (0.42, 0.66), "demand": 0.48,
        "mods": ["심플", "프리미엄", "데스크", "투명", "컬러", "대용량", "비즈니스", "스마트"],
        "items": ["노트", "펜", "파일", "스탠드", "캘린더", "파우치", "라벨지", "보드"],
        "opts": ["블랙", "화이트", "10입", "세트", "리필"],
    },
}


def round_100(value: float) -> int:
    return int(max(100, round(value / 100) * 100))


product_rows = []
product_seq = 1
for category, cfg in CATEGORY_CONFIG.items():
    combos = [f"{m} {item} {opt}" for m in cfg["mods"] for item in cfg["items"] for opt in cfg["opts"]]
    rng.shuffle(combos)
    for i in range(cfg["n"]):
        low, high = cfg["price"]
        price = round_100(rng.uniform(low, high))
        if price >= 10_000 and rng.random() < 0.35:
            price = int(price // 1_000 * 1_000 - 100)
        cost_ratio = rng.uniform(*cfg["cost_ratio"])
        cost = min(round_100(price * cost_ratio), price - 100)
        product_rows.append({
            "product_id": f"P{product_seq:05d}",
            "product_name": combos[i],
            "category": category,
            "price": int(price),
            "cost": int(cost),
            "_category_demand": cfg["demand"],
            "_product_weight": float(cfg["demand"] * rng.lognormal(0, 0.38) * (1 / np.sqrt(max(price, 1) / 10_000))),
        })
        product_seq += 1

products_work = pd.DataFrame(product_rows)
if len(products_work) != N_PRODUCTS:
    raise RuntimeError(f"상품 수가 {N_PRODUCTS}개가 아닙니다: {len(products_work)}")

products = products_work[["product_id", "product_name", "category", "price", "cost"]].copy()


# ---- 주문 fact ----
GRADE_ORDER_MULT = {"브론즈": 0.68, "실버": 1.00, "골드": 1.55, "VIP": 2.55}
GRADE_CATEGORY_MULT = {
    "브론즈": {"식품": 1.18, "생활용품": 1.08, "디지털": 0.72, "패션": 0.96, "뷰티": 0.92},
    "실버": {"식품": 1.04, "생활용품": 1.02, "디지털": 0.90, "패션": 1.02, "뷰티": 1.04},
    "골드": {"식품": 0.95, "생활용품": 0.96, "디지털": 1.18, "패션": 1.14, "뷰티": 1.16},
    "VIP": {"식품": 0.86, "생활용품": 0.90, "디지털": 1.62, "패션": 1.22, "뷰티": 1.20},
}
MONTH_CATEGORY_MULT = {
    1: {"생활용품": 1.10, "식품": 1.08},
    2: {"뷰티": 1.08, "식품": 1.05},
    3: {"문구/오피스": 1.75, "패션": 1.08},
    4: {"스포츠": 1.12, "패션": 1.08},
    5: {"뷰티": 1.20, "유아동": 1.18},
    6: {"스포츠": 1.18, "생활용품": 1.06},
    7: {"스포츠": 1.30, "디지털": 1.08},
    8: {"식품": 1.14, "스포츠": 1.10},
    9: {"식품": 1.25, "유아동": 1.12},
    10: {"패션": 1.18, "뷰티": 1.08},
    11: {"디지털": 1.55, "패션": 1.24},
    12: {"디지털": 1.35, "뷰티": 1.20, "식품": 1.18},
}

category_names = list(CATEGORY_CONFIG.keys())
base_category_weights = np.array([CATEGORY_CONFIG[c]["demand"] for c in category_names], dtype=float)
products_by_category = {
    c: products_work.loc[products_work["category"] == c].reset_index(drop=True)
    for c in category_names
}

customer_work = customers.copy()
customer_work["_join_date"] = pd.to_datetime(customer_work["join_date"]).to_numpy(dtype="datetime64[D]")
customer_work["_order_weight"] = (
    customer_work["grade"].map(GRADE_ORDER_MULT).astype(float).to_numpy()
    * customer_work["region"].map(REGION_ORDER_MULT).astype(float).to_numpy()
    * np.where(customer_work["age"].between(30, 49), 1.12, np.where(customer_work["age"] >= 50, 0.94, 0.88))
    * rng.lognormal(0, 0.22, size=N_CUSTOMERS)
)

all_order_dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
month_weight = all_order_dates.month.map({
    1: 0.88, 2: 0.82, 3: 0.94, 4: 0.98, 5: 1.05, 6: 0.96,
    7: 1.02, 8: 1.00, 9: 1.08, 10: 1.03, 11: 1.35, 12: 1.28,
}).to_numpy(dtype=float)
weekday_weight = np.where(all_order_dates.weekday >= 5, 1.16, 1.00)
payday_weight = np.where((all_order_dates.day >= 24) & (all_order_dates.day <= 26), 1.18, 1.00)
date_probs = month_weight * weekday_weight * payday_weight
date_probs = date_probs / date_probs.sum()

picked_dates = rng.choice(all_order_dates.to_numpy(dtype="datetime64[D]"), size=N_ORDERS, p=date_probs)
picked_dates.sort()
picked_dates[0] = np.datetime64("2024-01-01")
picked_dates[-1] = np.datetime64("2024-12-31")

customer_ids_arr = customer_work["customer_id"].to_numpy()
join_arr = customer_work["_join_date"].to_numpy(dtype="datetime64[D]")
customer_weight_arr = customer_work["_order_weight"].to_numpy(dtype=float)

order_rows = []
for i, order_date in enumerate(picked_dates, start=1):
    eligible = join_arr <= order_date
    weights = customer_weight_arr * eligible
    customer_idx = int(rng.choice(N_CUSTOMERS, p=weights / weights.sum()))
    customer = customer_work.iloc[customer_idx]
    grade = str(customer["grade"])

    cat_weights = base_category_weights.copy()
    for idx, cat in enumerate(category_names):
        cat_weights[idx] *= GRADE_CATEGORY_MULT.get(grade, {}).get(cat, 1.0)
        cat_weights[idx] *= MONTH_CATEGORY_MULT.get(pd.Timestamp(order_date).month, {}).get(cat, 1.0)
    cat_weights = cat_weights / cat_weights.sum()
    category = str(rng.choice(category_names, p=cat_weights))

    product_pool = products_by_category[category]
    product_probs = product_pool["_product_weight"].to_numpy(dtype=float)
    product_probs = product_probs / product_probs.sum()
    product = product_pool.iloc[int(rng.choice(len(product_pool), p=product_probs))]

    if category == "디지털":
        qty_probs = [0.92, 0.07, 0.01, 0.00]
    elif category in ["식품", "생활용품", "문구/오피스"]:
        qty_probs = [0.58, 0.27, 0.11, 0.04]
    else:
        qty_probs = [0.70, 0.21, 0.07, 0.02]
    if grade in ["골드", "VIP"] and category != "디지털":
        qty_probs = np.array(qty_probs, dtype=float) + np.array([-0.04, 0.02, 0.015, 0.005])
        qty_probs = (qty_probs / qty_probs.sum()).tolist()
    qty = int(rng.choice([1, 2, 3, 4], p=qty_probs))

    if grade == "브론즈":
        discount_choices = [0.00, 0.03, 0.05, 0.10]
        discount_probs = [0.74, 0.13, 0.10, 0.03]
    elif grade == "실버":
        discount_choices = [0.00, 0.03, 0.05, 0.10, 0.15]
        discount_probs = [0.57, 0.12, 0.20, 0.09, 0.02]
    elif grade == "골드":
        discount_choices = [0.00, 0.05, 0.10, 0.15]
        discount_probs = [0.36, 0.34, 0.22, 0.08]
    else:
        discount_choices = [0.00, 0.05, 0.10, 0.15, 0.20]
        discount_probs = [0.22, 0.30, 0.27, 0.16, 0.05]

    discount_rate = float(rng.choice(discount_choices, p=discount_probs))
    if pd.Timestamp(order_date).month in [11, 12] and rng.random() < 0.18:
        discount_rate = min(0.25, discount_rate + 0.05)

    order_rows.append({
        "order_id": f"O2024{i:06d}",
        "customer_id": str(customer_ids_arr[customer_idx]),
        "product_id": str(product["product_id"]),
        "order_date": pd.Timestamp(order_date).strftime("%Y-%m-%d"),
        "qty": qty,
        "discount_rate": round(discount_rate, 2),
    })

orders = pd.DataFrame(order_rows)


# ---- clean 저장 ----
orders_path = os.path.join(OUT, "orders.csv")
customers_path = os.path.join(OUT, "customers.csv")
products_path = os.path.join(OUT, "products.csv")
xlsx_path = os.path.join(OUT, "shop_orders_clean.xlsx")

orders.to_csv(orders_path, index=False, encoding="utf-8-sig")
customers.to_csv(customers_path, index=False, encoding="utf-8-sig")
products.to_csv(products_path, index=False, encoding="utf-8-sig")

with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
    orders.to_excel(writer, index=False, sheet_name="orders")
    customers.to_excel(writer, index=False, sheet_name="customers")
    products.to_excel(writer, index=False, sheet_name="products")


# ---- 재로드 검증 ----
orders_r = pd.read_csv(orders_path)
customers_r = pd.read_csv(customers_path)
products_r = pd.read_csv(products_path)
xlsx_r = pd.read_excel(xlsx_path, sheet_name=None)

fact = (
    orders_r
    .merge(customers_r, on="customer_id", how="left")
    .merge(products_r, on="product_id", how="left")
)
fact["gross_sales"] = fact["qty"] * fact["price"]
fact["net_sales"] = (fact["gross_sales"] * (1 - fact["discount_rate"])).round().astype(int)
fact["gross_profit"] = fact["net_sales"] - (fact["qty"] * fact["cost"])

missing_customer = int((~orders_r["customer_id"].isin(customers_r["customer_id"])).sum())
missing_product = int((~orders_r["product_id"].isin(products_r["product_id"])).sum())
invalid_order_date = int((pd.to_datetime(orders_r["order_date"]) < pd.Timestamp("2024-01-01")).sum() + (pd.to_datetime(orders_r["order_date"]) > pd.Timestamp("2024-12-31")).sum())
orders_before_join = int((pd.to_datetime(fact["order_date"]) < pd.to_datetime(fact["join_date"])).sum())
invalid_cost = int((products_r["cost"] >= products_r["price"]).sum())
duplicate_order_id = int(orders_r["order_id"].duplicated().sum())
duplicate_customer_id = int(customers_r["customer_id"].duplicated().sum())
duplicate_product_id = int(products_r["product_id"].duplicated().sum())

grade_summary = (
    fact.groupby("grade", as_index=False)
    .agg(orders=("order_id", "count"), net_sales=("net_sales", "sum"), avg_net_order=("net_sales", "mean"))
    .sort_values("net_sales", ascending=False)
)
region_summary = (
    fact.groupby("region", as_index=False)
    .agg(orders=("order_id", "count"), net_sales=("net_sales", "sum"))
    .sort_values("net_sales", ascending=False)
    .head(5)
)
category_summary = (
    fact.groupby("category", as_index=False)
    .agg(orders=("order_id", "count"), net_sales=("net_sales", "sum"), gross_profit=("gross_profit", "sum"))
    .sort_values("net_sales", ascending=False)
)

print("=== shop_orders 생성 완료 ===")
print(f"seed: {SEED}")
print(f"산출 위치: {os.path.abspath(OUT)}")
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    print(f"  - {f} ({os.path.getsize(p):,} bytes)")

print("\n=== 재로드 shape/head(3) 검증 ===")
for name, df in [("orders", orders_r), ("customers", customers_r), ("products", products_r)]:
    print(f"\n[{name}] shape={df.shape}")
    print(df.head(3).to_string(index=False))

print("\n[xlsx] sheet shapes")
for sheet_name, df in xlsx_r.items():
    print(f"  - {sheet_name}: {df.shape}")

print("\n=== clean 관계/품질 함정 실측 ===")
print(f"orders.customer_id 미매칭: {missing_customer}")
print(f"orders.product_id 미매칭: {missing_product}")
print(f"order_date 2024년 범위 밖: {invalid_order_date}")
print(f"order_date가 join_date보다 빠른 행: {orders_before_join}")
print(f"order_id 중복: {duplicate_order_id}")
print(f"customer_id 중복: {duplicate_customer_id}")
print(f"product_id 중복: {duplicate_product_id}")
print(f"cost >= price 상품: {invalid_cost}")
print("dirty 함정: 없음(clean만 생성)")

print("\n=== 내장 매출 차이 패턴 실측 ===")
print("[등급별 순매출]")
print(grade_summary.to_string(index=False, formatters={
    "net_sales": "{:,.0f}".format,
    "avg_net_order": "{:,.0f}".format,
}))
print("\n[지역별 순매출 TOP 5]")
print(region_summary.to_string(index=False, formatters={"net_sales": "{:,.0f}".format}))
print("\n[카테고리별 순매출]")
print(category_summary.to_string(index=False, formatters={
    "net_sales": "{:,.0f}".format,
    "gross_profit": "{:,.0f}".format,
}))
