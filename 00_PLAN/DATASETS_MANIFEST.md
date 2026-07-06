# 예시 데이터셋 매니페스트

> 모든 데이터셋은 `02_datasets/_generators/`의 파이썬 스크립트로 시드 고정 생성. **BI-ready 규칙**: 시트당 표 1개 · 헤더 1행 · 병합셀 금지 · long format · 컬럼명 영문 snake + 한글 헤더 병기 없음(BI 호환).

## 공통 규칙
- 인코딩: UTF-8(CSV) / xlsx
- 날짜: `YYYY-MM-DD` (clean) — dirty는 형식 혼합
- 통화: 원(KRW) 정수, 통화기호 없음(clean)
- 결측: clean=없음, dirty=의도적 심기

---

## 1. cafe_sales — 카페 매출 (메인 골격)

한 카페의 일별·시간대별 주문 내역. 전 파트를 관통하는 중심 데이터.

**스키마 (거래 1건 = 1행, long format)**
| 컬럼 | 타입 | 설명 | 예 |
|---|---|---|---|
| order_id | int | 주문번호(고유) | 10001 |
| date | date | 주문일 | 2025-03-14 |
| weekday | str | 요일 | Fri |
| hour | int | 시각(0-23) | 14 |
| store | str | 지점 | 강남점 |
| category | str | 분류 | 커피/디저트/음료 |
| item | str | 메뉴명 | 아메리카노 |
| unit_price | int | 단가 | 4500 |
| qty | int | 수량 | 2 |
| amount | int | 금액(=unit_price*qty) | 9000 |
| payment | str | 결제수단 | 카드/현금/간편결제 |
| member | bool | 멤버십 여부 | TRUE |

- 규모: 약 6개월 × 2지점 ≈ 8,000행
- 계절/요일/시간대 패턴 내장(주말↑, 오후 피크, 여름 음료↑) → 시각화·통계에서 발견할 거리 확보

**cafe_sales_dirty 심을 함정**
- 결측: `payment` 일부 공백, `member` 일부 빈칸
- 중복: 동일 order_id 중복행 몇 건
- 형식 불일치: `date`에 `2025/03/14`·`3-14-2025` 혼입, `unit_price`에 `"4,500원"` 문자열 혼입
- 오타 범주: `아메리카노`/`아메리카`/`Americano` 혼재, `강남점`/`강남 점`
- 이상치: qty=999, amount 음수 1건
- 공백: 앞뒤 공백 있는 문자열

---

## 2. shop_orders — 쇼핑몰 (3테이블, 관계형)

merge/VLOOKUP과 BI 데이터 모델링(스타 스키마)용. 3개 파일(또는 3시트).

- `orders`: order_id, customer_id, product_id, order_date, qty, discount_rate
- `customers`: customer_id, name, gender, age, region, join_date, grade
- `products`: product_id, product_name, category, price, cost

→ 조인해서 "지역별 매출", "등급별 객단가", "카테고리 마진" 등 도출.

## 3. survey_responses — 설문 (범주·텍스트)

AI 노코드 분석·범주 처리용. dirty만 제작.
- respondent_id, age_group, gender, nps(0-10), satisfaction(1-5 척도, 일부 결측), channel, free_text(주관식 한국어), submitted_at
- 함정: 척도 혼입("매우만족"/5 섞임), 주관식 공백/이모지, 중복 응답

## 4. web_traffic — 월별 웹 트래픽 (시계열)

- date(월초), sessions, users, pageviews, bounce_rate, signups, channel(organic/paid/social/direct)
- 24개월 추세+계절성+캠페인 스파이크 1~2회 → 시계열 시각화·전월대비 DAX

## 5. hr_employees — 인사 (통계·이상치)

- emp_id, dept, position, gender, age, tenure_years, salary, eval_score, overtime_hours
- clean/dirty. 함정(dirty): salary 이상치, age 결측, dept 오타, eval_score 범위 초과
- 용도: 분포·박스플롯·상관(근속vs연봉)·심슨의 역설(부서별)

## 6. capstone — 통합 케이스

Part 6용. cafe_sales를 확장하거나 쇼핑몰 통합본으로, "원데이터→대시보드→보고" 풀사이클. Phase 1에서 확정.

---

## 생성 스크립트 규약
- 파일명: `gen_<dataset>.py`, 실행 시 `../<dataset>/` 하위에 clean/dirty 산출
- 시드: `SEED = 42` 고정
- 표준 출력에 행수·컬럼·심은 함정 요약 리포트
