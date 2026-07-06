from pathlib import Path

import pandas as pd


ROOT = Path("/mnt/d/ai-data-analysis-course")
SURVEY_CLEAN = ROOT / "02_datasets/survey_responses/survey_responses_clean.csv"
SURVEY_DIRTY = ROOT / "02_datasets/survey_responses/survey_responses_dirty.csv"
MOVIES = ROOT / "02_datasets/real_korean/movie_box/dacon_movies_train.csv"

EXPECTED_SURVEY_COLUMNS = [
    "respondent_id",
    "age_group",
    "gender",
    "nps",
    "satisfaction",
    "channel",
    "free_text",
    "submitted_at",
]


def nps_group(score: int) -> str:
    if score <= 6:
        return "비추천(0-6)"
    if score <= 8:
        return "중립(7-8)"
    return "추천(9-10)"


def classify_topic(text: str) -> str:
    rules = [
        ("배송/픽업", ["배송", "포장", "픽업", "기사님"]),
        (
            "고객지원/응대",
            ["고객센터", "상담", "문의", "답변", "처리", "교환", "환불", "반품", "응대", "문제 발생"],
        ),
        ("결제/혜택", ["결제", "쿠폰", "할인", "포인트", "혜택", "회원", "가격"]),
        ("상품정보/품질", ["상품 설명", "상품 비교", "품질", "실제 구성", "상세 페이지", "사진"]),
        ("매장/오프라인", ["매장", "오프라인", "재고", "헛걸음"]),
        ("알림/마케팅", ["알림", "푸시", "이벤트", "프로모션", "추천 상품"]),
        (
            "앱/사용성",
            ["모바일", "앱", "화면", "검색", "필터", "로딩", "메뉴", "디자인", "주소", "자동완성", "가입", "이전 구매", "예약", "정보", "글자"],
        ),
    ]
    for topic, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return topic
    return "기타"


def classify_text_sentiment(text: str) -> str:
    negative_or_improve = [
        "불편",
        "헷갈",
        "오류",
        "늦",
        "오래",
        "길",
        "복잡",
        "부담",
        "개선",
        "재시도",
        "어렵",
        "달라",
        "많아서",
        "더 좋",
        "있으면",
        "아쉬",
        "표시되면",
        "바꿨습니다",
    ]
    positive = [
        "좋",
        "편리",
        "정확",
        "만족",
        "쉬",
        "친절",
        "명확",
        "빨",
        "안심",
        "신뢰",
        "깔끔",
        "직관",
        "잘",
        "도움",
        "부담이 없",
        "해결",
        "일치",
    ]
    has_negative = any(word in text for word in negative_or_improve)
    has_positive = any(word in text for word in positive)
    if has_negative and has_positive:
        return "혼합/개선"
    if has_negative:
        return "부정/개선"
    if has_positive:
        return "긍정"
    return "중립"


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("|", "/") for col in cols) + " |")
    return "\n".join(lines)


def main() -> None:
    survey = pd.read_csv(SURVEY_CLEAN)
    dirty = pd.read_csv(SURVEY_DIRTY)
    movies = pd.read_csv(MOVIES)

    assert list(survey.columns) == EXPECTED_SURVEY_COLUMNS
    assert survey.shape == (1500, 8)
    assert dirty.shape == (1510, 8)
    assert movies.shape == (600, 12)
    assert survey["free_text"].isna().sum() == 0

    survey = survey.copy()
    survey["nps_group"] = survey["nps"].apply(nps_group)
    survey["topic_rule"] = survey["free_text"].apply(classify_topic)
    survey["text_sentiment_rule"] = survey["free_text"].apply(classify_text_sentiment)

    sample_parts = []
    for group in ["비추천(0-6)", "중립(7-8)", "추천(9-10)"]:
        part = survey.loc[survey["nps_group"] == group].sample(n=6, random_state=8)
        sample_parts.append(part)
    prompt_sample = pd.concat(sample_parts).sort_values(["nps", "respondent_id"])

    topic_summary = (
        survey.groupby("topic_rule")
        .agg(
            응답수=("respondent_id", "count"),
            평균NPS=("nps", "mean"),
            평균만족도=("satisfaction", "mean"),
        )
        .round({"평균NPS": 2, "평균만족도": 2})
        .sort_values(["응답수", "평균NPS"], ascending=[False, True])
        .reset_index()
        .rename(columns={"topic_rule": "주제"})
    )

    sentiment_summary = (
        survey["text_sentiment_rule"]
        .value_counts()
        .rename_axis("주관식_감성_휴리스틱")
        .reset_index(name="응답수")
    )

    dirty_issues = {
        "dirty_rows": len(dirty),
        "duplicated_respondent_id": int(dirty.duplicated("respondent_id").sum()),
        "missing_nps": int(dirty["nps"].isna().sum()),
        "missing_free_text": int(dirty["free_text"].isna().sum()),
        "non_numeric_satisfaction": int(pd.to_numeric(dirty["satisfaction"], errors="coerce").isna().sum()),
        "age_group_variants_for_20s": int(dirty["age_group"].isin(["20s", "이십대"]).sum()),
    }

    genre_summary = (
        movies.groupby("genre")
        .agg(영화수=("title", "count"), 평균관객수=("box_off_num", "mean"))
        .round({"평균관객수": 0})
        .astype({"평균관객수": "int64"})
        .sort_values("영화수", ascending=False)
        .head(5)
        .reset_index()
    )

    print("pandas version:", pd.__version__)
    print("survey clean shape:", survey.shape[0], "rows x", 8, "columns")
    print("survey dirty shape:", dirty.shape[0], "rows x", dirty.shape[1], "columns")
    print("dacon movies train shape:", movies.shape[0], "rows x", movies.shape[1], "columns")

    print("\n[dirty issue counts]")
    for key, value in dirty_issues.items():
        print(f"{key}: {value}")

    print("\n[NPS group counts]")
    print(survey["nps_group"].value_counts().reindex(["비추천(0-6)", "중립(7-8)", "추천(9-10)"]).to_string())

    print("\n[topic summary by simple rules]")
    print(topic_summary.to_string(index=False))

    print("\n[text sentiment summary by simple rules]")
    print(sentiment_summary.to_string(index=False))

    print("\n[prompt sample 18 rows]")
    sample_cols = ["respondent_id", "age_group", "channel", "nps", "satisfaction", "free_text"]
    print(markdown_table(prompt_sample[sample_cols]))

    print("\n[optional movie genre top 5]")
    print(genre_summary.to_string(index=False))


if __name__ == "__main__":
    main()
