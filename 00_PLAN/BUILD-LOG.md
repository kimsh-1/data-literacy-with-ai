# BUILD-LOG

## 2026-07-06
- Phase 0 데이터: codex 함대 15도메인 수집 → 실검증. 실데이터 52종 등재(REAL_DATA_CATALOG.md), 초소형 4개 폐기. cp949 19개 UTF-8 정규화(원본 1개 교육용 보존). 합성 4종(cafe_sales·shop_orders 3표 참조무결·survey·hr 심슨역설 실증) 생성·검증.
- Phase 1 설계: SESSIONS_SPEC.md 20차시 작성 → critic 3표 전원 REVISE. 결함 반영 v2 재작성: C1 기온-수요 상관축 붕괴→아파트 면적-가격/심슨으로 교체, M1 인코딩 정규화, S10 90분 확장, S16 날짜차원, S18 Looker 주력, S19 축소, 환경 선수조건. MASTERPLAN 동기화(20차시·web_traffic폐기·Copilot무료 정정).
- Phase 2 생성: 차시 20개 codex 팬아웃 발진(동시성15).
- Phase 2 완료: 20차시 × 4산출물(81 md) 생성. 2차 타임아웃(S05·S14) resume 재생성. 모범답안 코드 15개 전량 실행 통과.
- Phase 3 완료: 리뷰어 5개 적대검증(코드 실행·수치 실측 대조). 품질 견고(이모지0·지어낸출력0). 결함 HIGH 2건(S16/S17 날짜테이블 명명·S19/S20 상권/회귀 불일치)+minor 다수 → codex 14워커 병렬수리+S17 resume. 재검: S12 assert제거·S16 날짜테이블통일·S20 회귀제거·코드15개 재실행 통과. PHASE3_DEFECTS.md 기록.
- Phase 4 진행중: 윤문 워크플로우(20세션 산문 윤문→content-fidelity 검증). 원본 60개 _pre_yunmun_backup 백업.
- Phase 4 완료: 윤문 워크플로우 20/20 fidelity 통과. 스팟체크(수치생존·코드펜스무결·이모지0·코드15개 재실행) 통과.
- Phase 6 완료: 히어로+섹션 이미지 6장 codex 생성(Linear 톤, 제품급). assets/images/.
- Phase 8 완료: Linear 소개 사이트(site/index.html) designer 에이전트 제작, Playwright 3해상도 검증. SVG→실PNG 교체.
- Phase 9 완료: GitHub 공개 repo https://github.com/kimsh-1/data-literacy-with-ai (176파일, 실데이터 제외). Vercel 배포 라이브 https://site-opal-iota-97.vercel.app (HTML/이미지 200 확인).
- Phase 7 진행중: 30초 인트로 영상(hyperframes) 렌더 중 → 완성 시 사이트 슬롯 배선·재배포.
- Phase 7 완료: 30초 인트로 영상(intro.mp4, 1920x1080, 30.04s, h264+aac, Linear 모션그래픽). 프레임 실측검증. 사이트 <video> 배선 → Vercel 재배포 → GitHub 커밋/푸시.
- 전체 완료: GitHub https://github.com/kimsh-1/data-literacy-with-ai · Vercel https://site-opal-iota-97.vercel.app (영상 서빙 200 확인).
