# 실데이터 카탈로그 (REAL_DATA_CATALOG.md)

> codex 함대 수집 → pandas 실검증(워커 자가보고 불신) 통과분만 등재. 초소형/샘플 파일은 폐기.
> 유효 데이터셋 **52개** / 14도메인. 폐기 4개.
> 라이선스: 각 출처(공공데이터포털·서울열린데이터·국토부·기상청·KOBIS·NHIS·FRED·Kaggle/GitHub 미러) 약관 준수. **공개 repo에는 원본 미포함 — 출처링크+다운로드 스크립트로 대체.**

## 이커머스(해외 프록시) (비한국 프록시: 관계형 실습용)  `retail_ecommerce/`
- **olist_order_items_dataset.csv** — 112,650행 × 7열
  - 컬럼: order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value
- **olist_order_payments_dataset.csv** — 103,886행 × 5열
  - 컬럼: order_id, payment_sequential, payment_type, payment_installments, payment_value
- **online_retail_uci.xlsx** — 100,000행 × 8열
  - 컬럼: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
- **olist_orders_dataset.csv** — 99,441행 × 8열
  - 컬럼: order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date

## 서울 생활인구  `seoul_living_pop/`
- **seoul_living_population_gu_korean.csv** — 108,600행 × 32열
  - 컬럼: 기준일ID, 시간대구분, 자치구코드, 총생활인구수, 남자0세부터9세생활인구수, 남자10세부터14세생활인구수, 남자15세부터19세생활인구수, 남자20세부터24세생활인구수 …
- **seoul_living_population_gu_long_foreigner.csv** — 108,600행 × 6열
  - 컬럼: 기준일ID, 시간대구분, 자치구코드, 총생활인구수, 중국인체류인구수, 중국외외국인체류인구수
- **seoul_living_population_gu_temp_foreigner.csv** — 108,600행 × 6열
  - 컬럼: 기준일ID, 시간대구분, 자치구코드, 총생활인구수, 중국인체류인구수, 중국외외국인체류인구수
- **seoul_living_population_gu_daily.csv** — 77,792행 × 15열
  - 컬럼: 기준일ID, 시군구코드, 시군구명, 총생활인구수, 내국인생활인구수, 장기체류외국인인구수, 단기체류외국인인구수, 일최대인구수 …

## 배달/음식 주문  `delivery_food/`
- **chicken_order_decision_tree_table.csv** — 200,000행 × 8열
  - 컬럼: DAYOFWEEK, GENDER, AGE, GU, Temperature, Rainfall, game_count, CALLCNT
- **sk_delivery_call_2019_01.csv** — 108,375행 × 8열
  - 컬럼: 일자, 요일, 시간대, 업종, 시도, 시군구, 읍면동, 통화건수
- **food_delivery_prediction_raw_data2.csv** — 1,947행 × 15열
  - 컬럼: 일자, 통화건수, 한국은행 기준금리, 지점, 평균기온(°C), 최저기온(°C), 최고기온(°C), 일강수량(mm) …
- **food_delivery_prediction_raw_data.csv** — 1,857행 × 15열
  - 컬럼: Unnamed: 0, 통화건수, 한국은행 기준금리, 지점, 평균기온(°C), 최저기온(°C), 최고기온(°C), 일강수량(mm) …

## 서울 따릉이(공공자전거)  `seoul_bike/`
- **seoul_bike_od_by_time.csv** — 200,000행 × 10열
  - 컬럼: 기준_날짜, 집계_기준, 기준_시간대, 시작_대여소_ID, 시작_대여소명, 종료_대여소_ID, 종료_대여소명, 전체_건수 …
- **seoul_bike_usage_monthly_2022_01.csv** — 96,823행 × 11열
  - 컬럼: 대여일자, 대여소번호, 대여소명, 대여구분코드, 성별, 연령대코드, 이용건수, 운동량 …
- **seoul_bike_station_stats_2018.xlsx** — 7,012행 × 5열
  - 컬럼: 대여일자, 대여소번호, 대여소, 대여건수, 반납건수
- **seoul_bike_station_master.csv** — 3,157행 × 5열
  - 컬럼: 대여소_ID, 주소1, 주소2, 위도, 경도

## 서울 지하철 승하차  `seoul_subway/`
- **seoulmetro_daily_hourly_2025.csv** — 199,424행 × 26열
  - 컬럼: 연번, 수송일자, 호선, 역번호, 역명, 승하차구분, 06시이전, 06-07시간대 …
- **seoulmetro_daily_hourly_2023_11_2024_01.csv** — 50,238행 × 26열
  - 컬럼: 연번, 날짜, 호선, 역번호, 역명, 구분, 06시 이전, 06시-07시 …
- **seoul_subway_monthly_hourly_20210705.csv** — 45,338행 × 52열
  - 컬럼: 사용월, 호선명, 지하철역, 04시-05시 승차인원, 04시-05시 하차인원, 05시-06시 승차인원, 05시-06시 하차인원, 06시-07시 승차인원 …
- **seoul_subway_monthly_hourly_2017_api_mirror.csv** — 6,892행 × 52열
  - 컬럼: Unnamed: 0, USE_MON, LINE_NUM, SUB_STA_NM, FOUR_RIDE_NUM, FOUR_ALIGHT_NUM, FIVE_RIDE_NUM, FIVE_ALIGHT_NUM …

## 교통사고(TAAS·경찰)  `traffic_accident/`
- **police_traffic_accident_2014.xlsx** — 100,000행 × 5열
  - 컬럼: ACC_YM, BJD_CD, HIT_BJD_CD, ACC_STU, ACC_TYP_CD
- **taas_traffic_accidents_2019_2021.csv** — 61,415행 × 24열
  - 컬럼: 사고번호, 사고일시, 요일, 시군구, 사고내용, 사망자수, 중상자수, 경상자수 …
- **daegu_traffic_accident_eclo_train_2019_2021.csv** — 39,609행 × 23열
  - 컬럼: ID, 사고일시, 요일, 기상상태, 시군구, 도로형태, 노면상태, 사고유형 …
- **child_fatal_traffic_accidents_2015_2019.csv** — 423행 × 25열
  - 컬럼: 발생년, 발생년월일시, 발생시, 주야, 요일, 사망자수, 부상자수, 중상자수 …

## 상가업소/음식점  `cafe_restaurant/`
- **seoul_commercial_food_stores_202109_github.csv** — 119,158행 × 13열
  - 컬럼: 상가업소번호, 상호명, 지점명, 상권업종대분류명, 상권업종중분류명, 상권업종소분류명, 시도명, 시군구명 …
- **incheon_commercial_food_stores_202109_github.csv** — 36,932행 × 13열
  - 컬럼: 상가업소번호, 상호명, 지점명, 상권업종대분류명, 상권업종중분류명, 상권업종소분류명, 시도명, 시군구명 …

## 인구/고령화(행안부·KOSIS)  `population_kosis/`
- **mois_legal_dong_gender_age_population_20260531.csv** — 18,623행 × 231열
  - 컬럼: 법정동코드, 기준연월, 시도명, 시군구명, 읍면동명, 리명, 계, 남자 …
- **mois_legal_dong_gender_average_age_20260531.csv** — 18,623행 × 9열
  - 컬럼: 법정동코드, 기준연월, 시도명, 시군구명, 읍면동명, 리명, 전체 평균연령, 남자 평균연령 …
- **mois_admin_dong_gender_age_population_20260531.csv** — 3,618행 × 230열
  - 컬럼: 행정기관코드, 기준연월, 시도명, 시군구명, 읍면동명, 계, 남자, 여자 …
- **seogwipo_aging_ratio_aging_index_20250421.csv** — 17행 × 8열
  - 컬럼: 년도, 월, 서귀포시 인구수, 65세이상 인구수 , 14세이하 인구수, 고령화비율, 노령화지수, 데이터기준일자

## 아파트 실거래(국토부)  `realestate_apt/`
- **molit_apt_rent_seoul_gangnam_2024.csv** — 22,767행 × 21열
  - 컬럼: NO, 시군구, 번지, 본번, 부번, 단지명, 전월세구분, 전용면적(㎡) …
- **molit_apt_rent_busan_haeundae_2024.csv** — 8,700행 × 21열
  - 컬럼: NO, 시군구, 번지, 본번, 부번, 단지명, 전월세구분, 전용면적(㎡) …
- **molit_apt_sale_seoul_gangnam_2024.csv** — 3,754행 × 20열
  - 컬럼: NO, 시군구, 번지, 본번, 부번, 단지명, 전용면적(㎡), 계약년월 …
- **molit_apt_sale_busan_haeundae_2024.csv** — 3,248행 × 20열
  - 컬럼: NO, 시군구, 번지, 본번, 부번, 단지명, 전용면적(㎡), 계약년월 …

## 건강검진·의료(NHIS)  `public_health/`
- **nhis_ischemic_heart_disease_medical_use.csv** — 11,760행 × 11열
  - 컬럼: 발생년도, 성별, 5세 연령군, 소득수준, 광역시도, 광역시도명, 구시군, 인년 …
- **nhis_tumor_patients_by_year_age_gender_2024.csv** — 219행 × 5열
  - 컬럼: 구분, 진료개시년도, 연령, 성별, 환자수
- **nhis_health_checkup_by_insurance_gender_age_2023.csv** — 180행 × 34열
  - 컬럼: 검진사업년도, 직역, 연령(5세단위), 성별, 대상인원, 수검인원, 정상A, 정상B_실인원 …

## 코로나19(DS4C)  `covid_seoul/`
- **seoul_routes_ds4c.csv** — 2,822행 × 9열
  - 컬럼: global_id, local_id, start, end, type, latitude, longitude, province …
- **seoul_patients_ds4c.csv** — 282행 × 11열
  - 컬럼: local_id, global_id, country, sex, birth_year, infection_reason, infected_by, travel_history …
- **korea_covid19_policy_ds4c.csv** — 48행 × 7열
  - 컬럼: policy_id, country, type, gov_policy, detail, start_date, end_date

## 물가·환율·실업(FRED)  `prices_econ/`
- **fred_korea_cpi_all_items_monthly.csv** — 767행 × 2열
  - 컬럼: observation_date, KORCPIALLMINMEI
- **fred_korea_cpi_yoy_inflation_monthly.csv** — 767행 × 2열
  - 컬럼: observation_date, CPALTT01KRM659N
- **fred_korea_usd_krw_exchange_rate_monthly.csv** — 543행 × 2열
  - 컬럼: observation_date, EXKOUS
- **fred_korea_unemployment_rate_monthly.csv** — 323행 × 2열
  - 컬럼: observation_date, LRUN64TTKRM156S

## 기상 관측(기상청 ASOS)  `weather/`
- **kma_asos_daily_seoul_108_2024.csv** — 366행 × 14열
  - 컬럼: 일자, 지점번호, 일평균기온(C), 최고기온(C), 최저기온(C), 일강수량(mm), 일평균상대습도(%), 최저습도(%) …
- **kma_asos_daily_seoul_108_2021.csv** — 365행 × 14열
  - 컬럼: 일자, 지점번호, 일평균기온(C), 최고기온(C), 최저기온(C), 일강수량(mm), 일평균상대습도(%), 최저습도(%) …
- **kma_asos_daily_seoul_108_2022.csv** — 365행 × 14열
  - 컬럼: 일자, 지점번호, 일평균기온(C), 최고기온(C), 최저기온(C), 일강수량(mm), 일평균상대습도(%), 최저습도(%) …
- **kma_asos_daily_seoul_108_2023.csv** — 365행 × 14열
  - 컬럼: 일자, 지점번호, 일평균기온(C), 최고기온(C), 최저기온(C), 일강수량(mm), 일평균상대습도(%), 최저습도(%) …

## 영화 박스오피스  `movie_box/`
- **dacon_movies_train.csv** — 600행 × 12열
  - 컬럼: title, distributor, genre, release_time, time, screening_rat, director, dir_prev_bfnum …
- **dacon_movies_test.csv** — 243행 × 11열
  - 컬럼: title, distributor, genre, release_time, time, screening_rat, director, dir_prev_bfnum …
- **kobis_movie_info_2019.csv** — 208행 × 9열
  - 컬럼: movieCd, movieNm, movieNmEn, movieNmOg, watchGradeNm, openDt, showTm, genres …
- **kobis_weekly_boxoffice_2019.csv** — 208행 × 3열
  - 컬럼: movieCd, movieNm, audiAcc
