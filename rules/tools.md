# 툴 활용 가이드

## Codex 에이전트 우선 사용 작업
다음 작업은 반드시 Codex 에이전트에게 위임:
- pykrx / FinanceDataReader API 호출 및 데이터 수집
- SQLite CRUD 작업 (holdings, transactions, watchlist, budget 테이블)
- `wiki\portfolio\` MD 파일 동기화 (`scripts\sync_wiki.py` 실행)
- 수치 계산 및 데이터 가공
- 반복 실행이 필요한 모든 코드 작업

## Claude Sonnet 에이전트 담당 작업
- 뉴스·공시 텍스트 해석 및 요약
- 투자 논리 수립 및 검토
- 보고서 문장 작성
- 종목 정성 분석

## 데이터 수집 스크립트
- 시세·재무 데이터: `scripts\fetch.py` 함수 활용
- wiki 동기화: `scripts\sync_wiki.py` 실행

## API 사용 우선순위
1. `pykrx` — 당일 시세, 거래량, 시가총액
2. `FinanceDataReader` — 기간별 주가, 재무 데이터
3. `dart-fss` — 공시 검색 (DART_API_KEY 환경변수 필요)
4. 웹 크롤 — 위 API로 불가한 뉴스·분석 자료만

## 시스템 공통 에러 처리 정책

- **fetch.py 실패 시:** 전일 데이터로 대체하고 메시에게 즉시 에스컬레이션
- **sync_wiki.py 실패 시:** wiki 수동 업데이트 경고 후 계속 진행
- **DB 접근 실패 시:** 작업 중단 후 메시에게 보고, 데이터 추정 금지
- **WebSearch 실패 시:** 최대 2회 재시도 후 이전 분석 데이터 사용
