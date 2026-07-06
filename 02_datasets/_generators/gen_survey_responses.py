# -*- coding: utf-8 -*-
"""
survey_responses 데이터 생성기
- clean: 고객만족 설문 원본 스키마를 지킨 BI-ready 버전 (xlsx + csv)
- dirty: AI 노코드 분석/정제 실습용 함정을 심은 버전 (xlsx + csv)
실행: python gen_survey_responses.py
산출: ../survey_responses/survey_responses_clean.{xlsx,csv}, survey_responses_dirty.{xlsx,csv}
"""
import os
import re
from datetime import timedelta

import numpy as np
import pandas as pd
from openpyxl import load_workbook

SEED = 42
rng = np.random.default_rng(SEED)
OUT = os.path.join(os.path.dirname(__file__), "..", "survey_responses")
os.makedirs(OUT, exist_ok=True)

N = 1500
START = pd.Timestamp("2025-03-01 09:00:00")
END = pd.Timestamp("2025-05-31 23:30:00")

AGE_GROUPS = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
GENDERS = ["여성", "남성", "응답하지 않음"]
CHANNELS = ["네이버 검색", "카카오톡 채널", "인스타그램", "지인 추천", "오프라인 매장", "이메일", "앱 푸시"]
SATISFACTION_LABELS = ["매우불만족", "불만족", "보통", "만족", "매우만족"]
EMOJI_PATTERN = re.compile(r"[\U0001F300-\U0001FAFF]")

TEXT_POOL = [
    "상담 답변이 빨랐고 처리 과정이 깔끔했습니다.",
    "앱에서 필요한 정보를 찾기 쉬워서 만족합니다.",
    "결제 단계가 단순해서 다시 이용할 것 같습니다.",
    "배송 안내 문자가 제때 와서 안심이 됐습니다.",
    "가격 대비 품질이 좋아서 주변에 추천했습니다.",
    "처음 이용했는데 가입 절차가 어렵지 않았습니다.",
    "문의 남긴 뒤 안내가 조금 늦어서 아쉬웠습니다.",
    "쿠폰 적용 방법이 더 잘 보이면 좋겠습니다.",
    "직원 응대가 친절했고 설명도 이해하기 쉬웠습니다.",
    "상품 설명과 실제 구성이 거의 같아서 신뢰가 갔습니다.",
    "모바일 화면에서 버튼 위치가 조금 헷갈렸습니다.",
    "재고 안내가 정확해서 헛걸음하지 않았습니다.",
    "문제 발생 후 처리 결과를 끝까지 알려줘서 좋았습니다.",
    "회원 혜택이 명확해서 계속 이용할 생각입니다.",
    "알림이 너무 자주 와서 설정을 바꿨습니다.",
    "검색 결과가 원하는 순서로 나오지 않아 불편했습니다.",
    "포장 상태가 깔끔했고 파손 없이 도착했습니다.",
    "환불 절차가 예상보다 오래 걸렸습니다.",
    "이벤트 안내가 실제 구매에 도움이 됐습니다.",
    "고객센터 연결까지 대기 시간이 길었습니다.",
    "오프라인 매장에서 안내받은 내용과 앱 정보가 일치했습니다.",
    "주문 변경이 바로 반영돼서 편리했습니다.",
    "혜택 조건이 복잡해서 한 번 더 확인해야 했습니다.",
    "전체적으로 안정적이지만 로딩 속도는 개선되면 좋겠습니다.",
    "필요한 메뉴가 눈에 잘 들어와서 사용하기 편했습니다.",
    "예약 확인 화면이 직관적이라 실수가 줄었습니다.",
    "신규 고객용 안내가 조금 더 자세했으면 합니다.",
    "상담 기록이 남아 있어서 같은 설명을 반복하지 않아도 됐습니다.",
    "할인 금액이 결제 전 명확하게 보여서 좋았습니다.",
    "배송 예정일이 실제와 달라 일정 조정이 필요했습니다.",
    "교환 신청 화면이 간단해서 부담이 없었습니다.",
    "사용 중 오류가 한 번 있었지만 재접속 후 해결됐습니다.",
    "추천 상품이 제 관심사와 잘 맞았습니다.",
    "매장 직원이 대안을 제시해줘서 문제를 빨리 해결했습니다.",
    "영수증과 결제 내역 확인이 쉬웠습니다.",
    "회원 등급 설명이 한눈에 들어오지 않았습니다.",
    "문의 유형을 고르는 단계가 많아서 시간이 걸렸습니다.",
    "포인트 적립 내역이 바로 보여서 만족했습니다.",
    "프로모션 문구가 이해하기 쉬웠습니다.",
    "상세 페이지 사진이 충분해서 구매 결정에 도움이 됐습니다.",
    "앱 푸시로 받은 혜택을 바로 사용할 수 있어 편했습니다.",
    "배송 기사님 요청사항 반영이 잘 됐습니다.",
    "첫 화면에 정보가 많아서 조금 복잡하게 느껴졌습니다.",
    "이전 구매 내역을 기준으로 다시 주문하기 편했습니다.",
    "고객센터 답변이 정중했지만 해결까지 시간이 걸렸습니다.",
    "품절 대체 안내가 빨라서 불편이 적었습니다.",
    "매장 픽업 시간이 정확하게 안내됐습니다.",
    "상품 비교 기능이 있으면 더 좋겠습니다.",
    "카카오톡으로 문의하니 답변 확인이 편했습니다.",
    "가입 후 첫 구매 혜택이 명확해서 좋았습니다.",
    "주소 입력 화면에서 자동완성이 잘 작동했습니다.",
    "반품 배송비 안내가 더 앞쪽에 있으면 좋겠습니다.",
    "서비스 품질은 좋지만 가격은 조금 부담됩니다.",
    "기존 고객에게도 혜택이 더 있으면 좋겠습니다.",
    "상담원이 상황을 잘 이해하고 해결책을 안내했습니다.",
    "검색 필터가 세분화되어 원하는 상품을 빨리 찾았습니다.",
    "결제 오류 안내가 구체적이지 않아 재시도했습니다.",
    "배송 완료 사진이 남아 있어 확인이 쉬웠습니다.",
    "앱 디자인이 깔끔하고 글자가 잘 보입니다.",
    "문의 접수 후 예상 처리 시간이 표시되면 좋겠습니다.",
]


def random_submitted_at(size: int) -> list[str]:
    total_minutes = int((END - START).total_seconds() // 60)
    minute_offsets = rng.integers(0, total_minutes + 1, size=size)
    submitted = [START + timedelta(minutes=int(m)) for m in minute_offsets]
    submitted.sort()
    return [ts.strftime("%Y-%m-%d %H:%M:%S") for ts in submitted]


def make_clean() -> pd.DataFrame:
    age_group = rng.choice(AGE_GROUPS, size=N, p=[0.05, 0.22, 0.27, 0.24, 0.16, 0.06])
    gender = rng.choice(GENDERS, size=N, p=[0.52, 0.45, 0.03])
    channel = rng.choice(CHANNELS, size=N, p=[0.28, 0.18, 0.16, 0.12, 0.10, 0.08, 0.08])
    satisfaction = rng.choice([1, 2, 3, 4, 5], size=N, p=[0.04, 0.10, 0.25, 0.38, 0.23]).astype(int)

    nps_base = np.select(
        [
            satisfaction == 1,
            satisfaction == 2,
            satisfaction == 3,
            satisfaction == 4,
            satisfaction == 5,
        ],
        [
            rng.integers(0, 4, size=N),
            rng.integers(1, 6, size=N),
            rng.integers(4, 8, size=N),
            rng.integers(7, 10, size=N),
            rng.integers(9, 11, size=N),
        ],
    )
    nps_noise = rng.choice([-1, 0, 0, 0, 1], size=N)
    nps = np.clip(nps_base + nps_noise, 0, 10).astype(int)

    text_idx = rng.integers(0, len(TEXT_POOL), size=N)
    free_text = [TEXT_POOL[i] for i in text_idx]

    return pd.DataFrame(
        {
            "respondent_id": [f"R2025-{i:06d}" for i in range(1, N + 1)],
            "age_group": age_group,
            "gender": gender,
            "nps": nps,
            "satisfaction": satisfaction,
            "channel": channel,
            "free_text": free_text,
            "submitted_at": random_submitted_at(N),
        }
    )


def sample_index(index, n: int, seed: int):
    return pd.Index(index).to_series().sample(n=n, random_state=seed).index


def make_dirty(clean: pd.DataFrame) -> pd.DataFrame:
    dirty = clean.copy()

    # pandas 3.0에서는 int 컬럼에 결측/문자열을 넣기 전 object 캐스팅이 필요하다.
    dirty["nps"] = dirty["nps"].astype(object)
    dirty["satisfaction"] = dirty["satisfaction"].astype(object)
    dirty["free_text"] = dirty["free_text"].astype(object)

    # 1) 중복 응답: 무작위 10건 복제
    dup = dirty.sample(10, random_state=SEED)
    dirty = pd.concat([dirty, dup], ignore_index=True)

    # 2) satisfaction 척도 혼합: 5%에 문자열 라벨 혼입
    sat_idx = sample_index(dirty.index, 75, 101)
    dirty.loc[sat_idx, "satisfaction"] = rng.choice(
        ["매우만족", "보통", "만족", "불만족"], size=len(sat_idx), p=[0.36, 0.34, 0.20, 0.10]
    )

    # 3) nps 일부 결측
    nps_idx = sample_index(dirty.index.difference(sat_idx), 60, 102)
    dirty.loc[nps_idx, "nps"] = np.nan

    # 4) age_group 표기 혼재: 20대 일부를 이십대/20s로 변경
    age_pool = dirty.index[dirty["age_group"] == "20대"]
    age_mixed_idx = sample_index(age_pool, min(90, len(age_pool)), 103)
    half = len(age_mixed_idx) // 2
    dirty.loc[age_mixed_idx[:half], "age_group"] = "이십대"
    dirty.loc[age_mixed_idx[half:], "age_group"] = "20s"

    # 5) 주관식 공백 및 이모지 혼입
    blank_idx = sample_index(dirty.index.difference(nps_idx), 45, 104)
    dirty.loc[blank_idx[: len(blank_idx) // 2], "free_text"] = ""
    dirty.loc[blank_idx[len(blank_idx) // 2 :], "free_text"] = "   "

    emoji_pool = dirty.index.difference(blank_idx)
    emoji_idx = sample_index(emoji_pool, 30, 105)
    emoji_suffixes = [
        " " + "\U0001F60A",
        " " + "\U0001F44D",
        " " + "\U0001F622",
        " " + "\U0001F914",
        " " + "\U0001F389",
    ]
    dirty.loc[emoji_idx, "free_text"] = [
        f"{text}{rng.choice(emoji_suffixes)}" for text in dirty.loc[emoji_idx, "free_text"].astype(str)
    ]

    # 행 순서 섞기(제출 순서 아님)
    dirty = dirty.sample(frac=1.0, random_state=106).reset_index(drop=True)
    return dirty


def save_outputs(clean: pd.DataFrame, dirty: pd.DataFrame) -> None:
    clean.to_csv(os.path.join(OUT, "survey_responses_clean.csv"), index=False, encoding="utf-8-sig")
    clean.to_excel(os.path.join(OUT, "survey_responses_clean.xlsx"), index=False, sheet_name="survey")
    dirty.to_csv(os.path.join(OUT, "survey_responses_dirty.csv"), index=False, encoding="utf-8-sig")
    dirty.to_excel(os.path.join(OUT, "survey_responses_dirty.xlsx"), index=False, sheet_name="survey")


def merged_range_count(path: str) -> int:
    workbook = load_workbook(path, read_only=False, data_only=True)
    try:
        return sum(len(sheet.merged_cells.ranges) for sheet in workbook.worksheets)
    finally:
        workbook.close()


def validate_outputs() -> None:
    clean_csv_path = os.path.join(OUT, "survey_responses_clean.csv")
    dirty_csv_path = os.path.join(OUT, "survey_responses_dirty.csv")
    clean_xlsx_path = os.path.join(OUT, "survey_responses_clean.xlsx")
    dirty_xlsx_path = os.path.join(OUT, "survey_responses_dirty.xlsx")

    clean_csv = pd.read_csv(clean_csv_path)
    dirty_csv = pd.read_csv(dirty_csv_path)
    clean_xlsx = pd.read_excel(clean_xlsx_path)
    dirty_xlsx = pd.read_excel(dirty_xlsx_path)

    free_text = dirty_csv["free_text"]
    blank_free_text = free_text.isna() | free_text.astype(str).str.strip().eq("")
    emoji_free_text = free_text.fillna("").astype(str).str.contains(EMOJI_PATTERN, regex=True)
    satisfaction_mixed = dirty_csv["satisfaction"].astype(str).isin(SATISFACTION_LABELS)
    duplicate_responses = dirty_csv.duplicated(subset=["respondent_id"])
    age_variant_counts = dirty_csv["age_group"].value_counts().reindex(["20대", "이십대", "20s"], fill_value=0)

    print("=== survey_responses 생성 완료 ===")
    print(f"clean csv shape: {clean_csv.shape} / xlsx shape: {clean_xlsx.shape}")
    print(f"dirty csv shape: {dirty_csv.shape} / xlsx shape: {dirty_xlsx.shape}")
    print("dirty head(3):")
    print(dirty_csv.head(3).to_string(index=False))
    print("심은 함정 실측:")
    print(f"- satisfaction 문자열 라벨 혼입: {int(satisfaction_mixed.sum())}건")
    print(f"- nps 결측: {int(dirty_csv['nps'].isna().sum())}건")
    print(f"- respondent_id 중복 응답: {int(duplicate_responses.sum())}건")
    print(f"- age_group 20대 계열 표기: {age_variant_counts.to_dict()}")
    print(f"- free_text 공백/결측: {int(blank_free_text.sum())}건")
    print(f"- free_text 이모지 포함: {int(emoji_free_text.sum())}건")
    print(
        "xlsx 병합셀 수: "
        f"clean={merged_range_count(clean_xlsx_path)}, dirty={merged_range_count(dirty_xlsx_path)}"
    )
    print(f"산출 위치: {os.path.abspath(OUT)}")
    for filename in sorted(os.listdir(OUT)):
        path = os.path.join(OUT, filename)
        print(f"  - {filename} ({os.path.getsize(path):,} bytes)")


if __name__ == "__main__":
    clean_df = make_clean()
    dirty_df = make_dirty(clean_df)
    save_outputs(clean_df, dirty_df)
    validate_outputs()
