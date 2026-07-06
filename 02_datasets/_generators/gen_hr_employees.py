# -*- coding: utf-8 -*-
"""
hr_employees 데이터 생성기
- clean: 깨끗한 BI-ready 버전 (xlsx + csv)
- dirty: 함정을 의도적으로 심은 실전 연습 버전 (xlsx + csv)
실행: python gen_hr_employees.py
산출: ../hr_employees/hr_employees_clean.{xlsx,csv}, hr_employees_dirty.{xlsx,csv}
"""
import os

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)
OUT = os.path.join(os.path.dirname(__file__), "..", "hr_employees")
os.makedirs(OUT, exist_ok=True)

# ---- 부서 구성: 남성은 고연봉 부서에 더 많이, 여성은 저연봉 부서에 더 많이 배치 ----
# 부서별로는 여성 평균 연봉이 남성보다 높도록 연봉식을 설계해 심슨의 역설을 만든다.
DEPTS = [
    {"dept": "개발본부", "base": 58_000_000, "male": 300, "female": 70, "tenure": 5.8, "ot": 24},
    {"dept": "데이터전략팀", "base": 54_000_000, "male": 180, "female": 70, "tenure": 5.0, "ot": 19},
    {"dept": "영업본부", "base": 48_000_000, "male": 130, "female": 110, "tenure": 5.2, "ot": 16},
    {"dept": "인사총무팀", "base": 42_000_000, "male": 50, "female": 130, "tenure": 5.5, "ot": 9},
    {"dept": "고객운영팀", "base": 38_000_000, "male": 40, "female": 120, "tenure": 4.4, "ot": 12},
]
POSITIONS = ["사원", "대리", "과장", "차장", "부장"]
POSITION_PREMIUM = {
    "사원": 0,
    "대리": 4_500_000,
    "과장": 10_500_000,
    "차장": 17_500_000,
    "부장": 27_000_000,
}


def choose_position(tenure_years):
    if tenure_years < 2.5:
        probs = [0.82, 0.16, 0.02, 0.00, 0.00]
    elif tenure_years < 5.0:
        probs = [0.24, 0.62, 0.13, 0.01, 0.00]
    elif tenure_years < 9.0:
        probs = [0.04, 0.25, 0.58, 0.12, 0.01]
    elif tenure_years < 13.0:
        probs = [0.01, 0.06, 0.32, 0.50, 0.11]
    else:
        probs = [0.00, 0.02, 0.12, 0.38, 0.48]
    return rng.choice(POSITIONS, p=probs)


rows = []
for spec in DEPTS:
    for gender, n in [("남성", spec["male"]), ("여성", spec["female"])]:
        for _ in range(n):
            tenure_shift = 0.65 if gender == "여성" else 0.0
            tenure_years = float(np.clip(rng.normal(spec["tenure"] + tenure_shift, 2.7), 0.2, 18.5))
            tenure_years = round(tenure_years, 1)
            age = int(np.clip(round(25 + tenure_years + rng.normal(3.8, 3.6)), 23, 59))
            position = choose_position(tenure_years)
            eval_mean = 3.35 + (0.12 if gender == "여성" else 0.0) + min(tenure_years, 10) * 0.018
            eval_score = float(np.clip(rng.normal(eval_mean, 0.48), 1.0, 5.0))
            eval_score = round(eval_score, 1)
            overtime_hours = int(np.clip(round(rng.normal(spec["ot"] + tenure_years * 0.25, 6.0)), 0, 70))

            salary = (
                spec["base"]
                + POSITION_PREMIUM[position]
                + tenure_years * 850_000
                + (eval_score - 3.0) * 2_200_000
                + overtime_hours * 80_000
                + (2_400_000 if gender == "여성" else 0)
                + rng.normal(0, 2_100_000)
            )
            salary = int(round(max(salary, 28_000_000) / 100_000) * 100_000)

            rows.append(
                {
                    "dept": spec["dept"],
                    "position": position,
                    "gender": gender,
                    "age": age,
                    "tenure_years": tenure_years,
                    "salary": salary,
                    "eval_score": eval_score,
                    "overtime_hours": overtime_hours,
                }
            )

clean = pd.DataFrame(rows)

# 부서별 평균은 여성이 높고, 전체 평균은 남성이 높도록 실제 평균을 확인하며 보정한다.
for spec in DEPTS:
    dept = spec["dept"]
    m = clean["dept"].eq(dept) & clean["gender"].eq("남성")
    f = clean["dept"].eq(dept) & clean["gender"].eq("여성")
    male_mean = clean.loc[m, "salary"].mean()
    female_mean = clean.loc[f, "salary"].mean()
    target_gap = 1_500_000
    if female_mean - male_mean < target_gap:
        add_amount = target_gap - (female_mean - male_mean)
        clean.loc[f, "salary"] = clean.loc[f, "salary"] + int(np.ceil(add_amount / 100_000) * 100_000)

overall_gap = (
    clean.loc[clean["gender"].eq("남성"), "salary"].mean()
    - clean.loc[clean["gender"].eq("여성"), "salary"].mean()
)
if overall_gap <= 1_000_000:
    raise RuntimeError("심슨의 역설 설계 실패: 전체 평균에서 남성 평균연봉이 충분히 높지 않습니다.")

clean = clean.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
clean.insert(0, "emp_id", [f"EMP{2025}{i:04d}" for i in range(1, len(clean) + 1)])
clean = clean[
    [
        "emp_id",
        "dept",
        "position",
        "gender",
        "age",
        "tenure_years",
        "salary",
        "eval_score",
        "overtime_hours",
    ]
]

# ---- clean 저장 ----
clean_csv = os.path.join(OUT, "hr_employees_clean.csv")
clean_xlsx = os.path.join(OUT, "hr_employees_clean.xlsx")
clean.to_csv(clean_csv, index=False, encoding="utf-8-sig")
clean.to_excel(clean_xlsx, index=False, sheet_name="employees")

# ---- dirty 버전: 함정 심기 ----
dirty = clean.copy()

# pandas 3.0 엄격 dtype 회피: int 컬럼에 NaN을 넣기 전 object로 캐스팅
dirty["age"] = dirty["age"].astype(object)

# 1) salary 이상치: 고액 4건, 저액 2건
high_salary_idx = dirty.sample(4, random_state=101).index
dirty.loc[high_salary_idx, "salary"] = [185_000_000, 198_000_000, 212_000_000, 240_000_000]
low_salary_idx = dirty.drop(high_salary_idx).sample(2, random_state=102).index
dirty.loc[low_salary_idx, "salary"] = [16_000_000, 18_000_000]

# 2) age 결측
age_missing_idx = dirty.sample(24, random_state=201).index
dirty.loc[age_missing_idx, "age"] = np.nan

# 3) dept 오타/표기 흔들림
dept_typo_map = {
    "개발본부": ["개발 본부", "개발부서"],
    "데이터전략팀": ["데이터 전략팀", "데이터전략"],
    "영업본부": ["영엽본부", "영업 본부"],
    "인사총무팀": ["인사총무 팀", "인사총무"],
    "고객운영팀": ["고객운영", "고객운영팀팀"],
}
typo_idx = dirty.sample(20, random_state=301).index
for idx in typo_idx:
    original = dirty.at[idx, "dept"]
    dirty.at[idx, "dept"] = rng.choice(dept_typo_map[original])

# 4) eval_score 범위 초과: 6과 0 혼입
eval_high_idx = dirty.sample(5, random_state=401).index
dirty.loc[eval_high_idx, "eval_score"] = 6
eval_low_idx = dirty.drop(eval_high_idx).sample(5, random_state=402).index
dirty.loc[eval_low_idx, "eval_score"] = 0

# 행 순서 섞기
dirty = dirty.sample(frac=1.0, random_state=501).reset_index(drop=True)

dirty_csv = os.path.join(OUT, "hr_employees_dirty.csv")
dirty_xlsx = os.path.join(OUT, "hr_employees_dirty.xlsx")
dirty.to_csv(dirty_csv, index=False, encoding="utf-8-sig")
dirty.to_excel(dirty_xlsx, index=False, sheet_name="employees")

# ---- 저장 후 재로드 검증 ----
clean_reload = pd.read_csv(clean_csv)
dirty_reload = pd.read_csv(dirty_csv)
valid_depts = [d["dept"] for d in DEPTS]

overall = clean_reload.groupby("gender")["salary"].mean().round(0).astype(int)
dept_gender = (
    clean_reload.pivot_table(index="dept", columns="gender", values="salary", aggfunc="mean")
    .loc[valid_depts]
    .round(0)
    .astype(int)
)
dept_gender["여성-남성"] = dept_gender["여성"] - dept_gender["남성"]

salary_outlier_count = (
    (dirty_reload["salary"] < 20_000_000) | (dirty_reload["salary"] > 150_000_000)
).sum()
age_missing_count = dirty_reload["age"].isna().sum()
dept_typo_count = (~dirty_reload["dept"].isin(valid_depts)).sum()
eval_bad = dirty_reload.loc[~dirty_reload["eval_score"].between(1, 5), "eval_score"]

print("=== hr_employees 생성 완료 ===")
print(f"clean: {clean_reload.shape[0]:,}행 × {clean_reload.shape[1]}열")
print(clean_reload.head(3).to_string(index=False))
print(f"dirty: {dirty_reload.shape[0]:,}행 × {dirty_reload.shape[1]}열")
print(dirty_reload.head(3).to_string(index=False))
print("심슨의 역설 검증(평균연봉):")
print(f"  전체: 남성 {overall['남성']:,}원 / 여성 {overall['여성']:,}원 / 남성-여성 {overall['남성'] - overall['여성']:,}원")
print(dept_gender.to_string())
print("dirty 함정 실측:")
print(f"  salary 이상치(<2천만 또는 >1억5천만): {salary_outlier_count}건")
print(f"  age 결측: {age_missing_count}건")
print(f"  dept 오타/비표준값: {dept_typo_count}건")
print(f"  eval_score 범위초과: {len(eval_bad)}건, 값분포 {eval_bad.value_counts().sort_index().to_dict()}")
print(f"산출 위치: {os.path.abspath(OUT)}")
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    print(f"  - {f} ({os.path.getsize(p):,} bytes)")
