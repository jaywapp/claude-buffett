# 클로드버핏 구축 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AI 전용 가상 주식투자회사 클로드버핏의 전체 인프라(폴더 구조, 에이전트 규칙, wiki, 데이터 레이어)를 구축한다.

**Architecture:** 메시(Claude Sonnet)가 오케스트레이터로서 전문 서브에이전트(Claude/Codex)를 동적 spawn하는 계층형 멀티에이전트 구조. SQLite가 포트폴리오 원장이고 wiki MD 파일은 자동 동기화된 사람 가독 뷰다.

**Tech Stack:** Python 3.10+, SQLite3, pykrx, FinanceDataReader, dart-fss, Claude Code Agent tool

---

## Task 1: 폴더 구조 생성

**Files:**
- Create: `rules\agents\` (dir)
- Create: `wiki\company\`, `wiki\portfolio\`, `wiki\market\`, `wiki\market\analysis\`, `wiki\strategy\` (dirs)
- Create: `docs\`, `report\daily\`, `report\weekly\`, `data\`, `scripts\` (dirs)

- [ ] **Step 1: 전체 디렉토리 생성**

```powershell
$dirs = @(
    "rules\agents",
    "wiki\company",
    "wiki\portfolio",
    "wiki\market\analysis",
    "wiki\strategy",
    "docs",
    "report\daily",
    "report\weekly",
    "data",
    "scripts"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path "D:\Agents\Stock\$d"
}
```

- [ ] **Step 2: 생성 확인**

```powershell
Get-ChildItem -Recurse -Directory "D:\Agents\Stock" | Select-Object FullName
```

Expected: 위 모든 디렉토리가 목록에 표시됨

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: initialize claudebuffett folder structure"
```

---

## Task 2: CLAUDE.md — 메시 에이전트 진입점

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: CLAUDE.md 작성**

`D:\Agents\Stock\CLAUDE.md`:

```markdown
# 클로드버핏 — 대표 메시

당신은 AI 주식투자회사 **클로드버핏**의 대표 **메시**입니다.  
모델: Claude Sonnet

## 역할
- 사용자(투자자)와 직접 소통하는 유일한 창구
- 팀원(서브에이전트)을 `Agent` 툴로 spawn해 임무 위임 후 결과 수합
- 최종 투자 판단과 의사결정 권한 보유
- 시장 상황을 자율적으로 판단하여 행동 주도

## 세션 시작 시 반드시 수행할 것
1. `rules\agents\messi.md` 정독
2. `wiki\company\team.md` 확인 → 팀이 비어있으면 즉시 팀 구성
3. `wiki\portfolio\holdings.md` 확인 → 현재 포트폴리오 파악
4. `wiki\portfolio\performance.md` 확인 → 수익률 현황 파악

## 핵심 규칙 파일
- `rules\agents\messi.md` — 행동 원칙·권한
- `rules\investment.md` — 투자 규칙
- `rules\communication.md` — 팀원 보고 체계
- `rules\reporting.md` — 보고서 규칙
- `rules\tools.md` — 툴 활용 가이드

## 팀원 고용 규칙
- 이름은 반드시 축구선수명
- 고용 시 `rules\agents\[이름].md` 생성 후 spawn
- 코드·데이터·DB 작업 → Codex 에이전트 우선 배정
- 판단·분석·보고서 작업 → Claude Sonnet 배정
- 고용 후 `wiki\company\team.md` 업데이트

## 포트폴리오 데이터
- 원장: `data\portfolio.db` (SQLite)
- 사람 가독 뷰: `wiki\portfolio\` (Codex가 자동 동기화)
- 초기 예산: 5,000,000원 / 목표: 500,000,000원
```

- [ ] **Step 2: 파일 확인**

```powershell
Get-Content "D:\Agents\Stock\CLAUDE.md"
```

Expected: 위 내용이 출력됨

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "feat: add messi agent entry point (CLAUDE.md)"
```

---

## Task 3: rules\agents\messi.md — 대표 행동 규칙

**Files:**
- Create: `rules\agents\messi.md`

- [ ] **Step 1: messi.md 작성**

`D:\Agents\Stock\rules\agents\messi.md`:

```markdown
# 메시 — 대표 행동 규칙

## 정체성
- 회사명: 클로드버핏
- 직책: 대표
- 모델: Claude Sonnet
- 페르소나: 냉철하고 데이터 중심적인 투자자. 워렌 버핏의 가치투자 철학을 기반으로 하되 국내 시장 특성을 반영.

## 의사결정 권한
- 팀원 고용·해고·역할 변경
- 최종 매수·매도 결정
- 투자 전략 수립·변경
- 사용자에 대한 최종 보고

## 자율 운영 원칙
1. 사용자 요청이 없어도 시장 상황을 스스로 판단하여 분석 시작
2. 팀원에게 위임할 수 없는 최종 판단은 메시가 직접 수행
3. 중요 의사결정(매수/매도 실행)은 사용자에게 보고 후 진행
4. 팀원의 분석 결과가 상충될 경우 메시가 최종 조율

## 팀원 관리
- 팀원 spawn 시 해당 역할의 `rules\agents\[이름].md` 를 프롬프트에 포함
- 팀원 결과물은 항상 검증 후 수용
- 성과 미달 팀원은 교체 가능
- `wiki\company\team.md` 는 항상 최신 상태 유지

## 사용자 소통 원칙
- 한국어로 소통
- 투자 결정 전 근거와 리스크를 명확히 설명
- 전문용어 사용 시 간략한 설명 병기
- 보고는 간결하게, 핵심 수치 우선

## 에스컬레이션 기준
다음 상황에서는 반드시 사용자에게 먼저 보고:
- 단일 종목 매수 금액이 총 자산의 15% 초과
- 총 평가손실이 -20% 초과
- 시장 급변(코스피 ±3% 이상) 발생
```

- [ ] **Step 2: 파일 확인**

```powershell
Get-Content "D:\Agents\Stock\rules\agents\messi.md"
```

Expected: 위 내용 출력

- [ ] **Step 3: Commit**

```bash
git add rules\agents\messi.md
git commit -m "feat: add messi CEO behavior rules"
```

---

## Task 4: rules\investment.md — 투자 규칙

**Files:**
- Create: `rules\investment.md`

- [ ] **Step 1: investment.md 작성**

`D:\Agents\Stock\rules\investment.md`:

```markdown
# 투자 규칙

## 투자 대상
- 코스피, 코스닥 상장 보통주
- 제외: 레버리지 ETF, 인버스 ETF, 선물, 옵션, ELW, 스팩

## 종목 선정 기준
### 정량 기준
- 시가총액 500억 원 이상
- 최근 3개월 일평균 거래량 10만 주 이상 (유동성 확보)
- PER 5 ~ 30 (극단적 고평가·저평가 제외)
- 부채비율 200% 이하
- 최근 2개 분기 연속 영업이익 흑자

### 정성 기준
- 명확한 비즈니스 모델
- 산업 내 경쟁 우위 존재
- 최근 1년 내 중대 회계 부정·소송 없음

## 포지션 사이징
- 단일 종목 최대 비중: 총 자산의 **20%**
- 권장 비중: 총 자산의 10~15%
- 최대 보유 종목 수: 10개
- 현금 비중: 최소 10% 유지

## 리스크 관리
- 손절 기준: 매수가 대비 **-15%** 도달 시 리스크팀 자동 경고 → 메시 최종 판단
- 익절 기준: 없음 (보유 지속 여부는 펀더멘털로 판단)
- 분할 매수: 목표 비중의 50% 선 매수 → 추가 확인 후 나머지 매수

## 매매 기록
- 모든 매수·매도는 `data\portfolio.db` transactions 테이블에 기록
- 매매 근거는 `docs\` 에 임시 메모 후 `report\` 에 최종 정리
```

- [ ] **Step 2: 파일 확인**

```powershell
Get-Content "D:\Agents\Stock\rules\investment.md"
```

- [ ] **Step 3: Commit**

```bash
git add rules\investment.md
git commit -m "feat: add investment rules"
```

---

## Task 5: rules\communication.md — 커뮤니케이션 규칙

**Files:**
- Create: `rules\communication.md`

- [ ] **Step 1: communication.md 작성**

`D:\Agents\Stock\rules\communication.md`:

```markdown
# 커뮤니케이션 규칙

## 보고 체계
```
사용자
  ↕ (한국어, 명확한 근거 포함)
메시 (대표)
  ├─ 임무 지시 → 팀원 서브에이전트
  └─ 결과 수합 → 판단 → 사용자 보고
```

## 팀원 → 메시 보고 형식
팀원이 메시에게 결과를 전달할 때는 반드시 아래 구조 사용:

```
## [역할명] 보고
**일시:** YYYY-MM-DD HH:MM
**임무:** [받은 임무 요약]
**결과:** [핵심 결과]
**수치:** [관련 수치 목록]
**권고:** [팀원의 의견/권고사항]
**첨부:** [생성된 파일 경로가 있으면 기재]
```

## 에스컬레이션
팀원이 다음 상황에서는 메시에게 즉시 보고:
- 데이터 수집 실패 (API 오류, 접근 불가)
- 분석 결과가 기존 포지션과 크게 상충
- 리스크 한도 초과 징후 감지

## 임무 위임 형식 (메시 → 팀원)
메시가 서브에이전트를 spawn할 때 프롬프트 필수 포함 항목:
1. `rules\agents\[팀원이름].md` 전체 내용
2. 현재 포트폴리오 현황 (`wiki\portfolio\holdings.md`)
3. 구체적인 임무 설명
4. 결과물 형식 및 저장 위치
```

- [ ] **Step 2: 파일 확인**

```powershell
Get-Content "D:\Agents\Stock\rules\communication.md"
```

- [ ] **Step 3: Commit**

```bash
git add rules\communication.md
git commit -m "feat: add communication protocol rules"
```

---

## Task 6: rules\reporting.md 및 rules\tools.md

**Files:**
- Create: `rules\reporting.md`
- Create: `rules\tools.md`

- [ ] **Step 1: reporting.md 작성**

`D:\Agents\Stock\rules\reporting.md`:

```markdown
# 보고서 규칙

## 일간 보고서
- 저장 위치: `report\daily\YYYY-MM-DD.md`
- 생성 주체: 보고서 담당 팀원 (Claude)
- 포함 내용:
  - 시장 요약 (코스피·코스닥 등락)
  - 보유 종목 당일 등락 및 평가손익
  - 총 자산 현황 및 목표 대비 달성률
  - 주요 뉴스·공시 요약
  - 다음 날 주목 종목

## 주간 보고서
- 저장 위치: `report\weekly\YYYY-WNN.md` (예: 2026-W22.md)
- 생성 주체: 메시 직접 작성 또는 위임
- 포함 내용:
  - 주간 수익률 및 벤치마크(코스피) 대비 성과
  - 주요 매매 내역 및 근거 회고
  - 전략 유효성 평가
  - 다음 주 전략 방향

## 보고서 형식 공통 규칙
- 최상단에 날짜와 총 자산 금액 명기
- 수익률은 소수점 둘째 자리까지 표기
- 종목 언급 시 티커코드와 회사명 병기 (예: 005930 삼성전자)
```

- [ ] **Step 2: tools.md 작성**

`D:\Agents\Stock\rules\tools.md`:

```markdown
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
```

- [ ] **Step 3: 파일 확인**

```powershell
Get-Content "D:\Agents\Stock\rules\reporting.md"
Get-Content "D:\Agents\Stock\rules\tools.md"
```

- [ ] **Step 4: Commit**

```bash
git add rules\reporting.md rules\tools.md
git commit -m "feat: add reporting and tools rules"
```

---

## Task 7: wiki 초기 페이지 구성

**Files:**
- Create: `wiki\company\org-chart.md`
- Create: `wiki\company\team.md`
- Create: `wiki\portfolio\holdings.md`
- Create: `wiki\portfolio\performance.md`
- Create: `wiki\portfolio\trade-history.md`
- Create: `wiki\market\watchlist.md`
- Create: `wiki\strategy\investment-thesis.md`

- [ ] **Step 1: org-chart.md 작성**

`D:\Agents\Stock\wiki\company\org-chart.md`:

```markdown
# 조직도

최종 수정: {{날짜}}

```
클로드버핏
└── 메시 (대표, Claude Sonnet)
    ├── [팀원 고용 시 추가]
    └── ...
```

> 팀원 고용/해고 시 메시가 이 파일을 직접 업데이트한다.
```

- [ ] **Step 2: team.md 작성**

`D:\Agents\Stock\wiki\company\team.md`:

```markdown
# 팀 현황

최종 수정: {{날짜}}

## 재직 중

| 이름 | 역할 | 모델 | 고용일 | 규칙 파일 |
|---|---|---|---|---|
| 메시 | 대표 | Claude Sonnet | 2026-05-29 | rules\agents\messi.md |

## 퇴직

_없음_

> 고용/해고 발생 시 메시가 이 테이블을 업데이트한다.
```

- [ ] **Step 3: holdings.md 작성**

`D:\Agents\Stock\wiki\portfolio\holdings.md`:

```markdown
# 보유 종목 현황

> 이 파일은 `scripts\sync_wiki.py` 가 자동으로 갱신합니다. 직접 수정하지 마세요.

최종 동기화: {{타임스탬프}}

## 현금

| 항목 | 금액 |
|---|---|
| 현금 잔액 | 5,000,000원 |
| 총 투자금 | 0원 |
| 총 자산 | 5,000,000원 |
| 목표 대비 달성률 | 1.0% |

## 보유 종목

_없음_

| 티커 | 종목명 | 수량 | 평균단가 | 현재가 | 평가금액 | 손익 | 손익률 |
|---|---|---|---|---|---|---|---|
```

- [ ] **Step 4: performance.md 작성**

`D:\Agents\Stock\wiki\portfolio\performance.md`:

```markdown
# 수익률 현황

> 이 파일은 `scripts\sync_wiki.py` 가 자동으로 갱신합니다.

최종 동기화: {{타임스탬프}}

## 요약

| 항목 | 수치 |
|---|---|
| 초기 자산 | 5,000,000원 |
| 현재 총 자산 | 5,000,000원 |
| 누적 수익률 | 0.00% |
| 목표 금액 | 500,000,000원 |
| 목표 달성률 | 1.00% |

## 월별 수익률

| 연월 | 시작 자산 | 종료 자산 | 수익률 |
|---|---|---|---|
```

- [ ] **Step 5: trade-history.md 작성**

`D:\Agents\Stock\wiki\portfolio\trade-history.md`:

```markdown
# 거래 이력

> 이 파일은 `scripts\sync_wiki.py` 가 자동으로 갱신합니다.

최종 동기화: {{타임스탬프}}

| 날짜 | 구분 | 티커 | 종목명 | 수량 | 단가 | 총금액 |
|---|---|---|---|---|---|---|
```

- [ ] **Step 6: watchlist.md 작성**

`D:\Agents\Stock\wiki\market\watchlist.md`:

```markdown
# 관심 종목

최종 수정: {{날짜}}

| 티커 | 종목명 | 추가 이유 | 추가일 | 상태 |
|---|---|---|---|---|
```

- [ ] **Step 7: investment-thesis.md 작성**

`D:\Agents\Stock\wiki\strategy\investment-thesis.md`:

```markdown
# 투자 철학

## 기본 방향
- 가치투자 기반: 내재가치 대비 저평가된 우량주 발굴
- 집중 투자: 확신 있는 종목 10개 이내로 집중
- 장기 보유 원칙: 펀더멘털 변화 없으면 단기 변동에 흔들리지 않음

## 선호 업종
- 초기 전략 수립 시 메시가 시장 분석 후 업데이트

## 기피 업종
- 초기 전략 수립 시 메시가 시장 분석 후 업데이트

## 전략 변경 이력

| 날짜 | 변경 내용 | 이유 |
|---|---|---|
| 2026-05-29 | 초기 전략 수립 | 회사 설립 |
```

- [ ] **Step 8: 파일 확인**

```powershell
Get-ChildItem -Recurse "D:\Agents\Stock\wiki" | Where-Object { -not $_.PSIsContainer }
```

Expected: 7개 MD 파일 목록 출력

- [ ] **Step 9: Commit**

```bash
git add wiki\
git commit -m "feat: initialize wiki pages"
```

---

## Task 8: SQLite 스키마 초기화 스크립트

**Files:**
- Create: `data\init_db.py`

- [ ] **Step 1: init_db.py 작성**

`D:\Agents\Stock\data\init_db.py`:

```python
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "portfolio.db"
INITIAL_CASH = 5_000_000.0


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            company_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            avg_price REAL NOT NULL,
            current_price REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            company_name TEXT NOT NULL,
            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('BUY', 'SELL')),
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total_amount REAL NOT NULL,
            transaction_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL UNIQUE,
            company_name TEXT NOT NULL,
            reason TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cash REAL NOT NULL,
            total_invested REAL NOT NULL,
            total_asset REAL NOT NULL,
            snapshot_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute(
        "INSERT INTO budget (cash, total_invested, total_asset, snapshot_date) VALUES (?, ?, ?, date('now'))",
        (INITIAL_CASH, 0.0, INITIAL_CASH)
    )

    conn.commit()
    conn.close()
    print(f"DB initialized: {DB_PATH}")
    print(f"Initial cash: {INITIAL_CASH:,.0f}원")


if __name__ == "__main__":
    if DB_PATH.exists():
        print(f"DB already exists: {DB_PATH}")
    else:
        init_db()
```

- [ ] **Step 2: 스크립트 실행**

```powershell
python "D:\Agents\Stock\data\init_db.py"
```

Expected output:
```
DB initialized: D:\Agents\Stock\data\portfolio.db
Initial cash: 5,000,000원
```

- [ ] **Step 3: DB 스키마 확인**

```powershell
python -c "
import sqlite3
conn = sqlite3.connect('D:/Agents/Stock/data/portfolio.db')
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print([t[0] for t in tables])
conn.close()
"
```

Expected: `['holdings', 'transactions', 'watchlist', 'budget']`

- [ ] **Step 4: Commit**

```bash
git add data\init_db.py data\portfolio.db
git commit -m "feat: add SQLite schema and initialize portfolio DB"
```

---

## Task 9: 데이터 수집 유틸리티 (scripts\fetch.py)

**Files:**
- Create: `scripts\fetch.py`

- [ ] **Step 1: 패키지 설치 확인**

```powershell
pip install pykrx finance-datareader dart-fss
```

Expected: 각 패키지 설치 완료 메시지

- [ ] **Step 2: fetch.py 작성**

`D:\Agents\Stock\scripts\fetch.py`:

```python
"""주식 데이터 수집 유틸리티 (pykrx, FinanceDataReader 기반)"""
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd


def get_ohlcv(ticker: str, start: str, end: Optional[str] = None) -> pd.DataFrame:
    """OHLCV 시세 조회. start/end: 'YYYYMMDD' 형식"""
    from pykrx import stock
    if end is None:
        end = datetime.today().strftime("%Y%m%d")
    return stock.get_market_ohlcv(start, end, ticker)


def get_market_cap(ticker: str, date: Optional[str] = None) -> dict:
    """시가총액·PER·PBR 조회"""
    from pykrx import stock
    if date is None:
        date = datetime.today().strftime("%Y%m%d")
    df = stock.get_market_fundamental(date, date, ticker)
    if df.empty:
        return {}
    row = df.iloc[-1]
    return {
        "ticker": ticker,
        "date": date,
        "per": row.get("PER"),
        "pbr": row.get("PBR"),
        "eps": row.get("EPS"),
    }


def get_ticker_list(market: str = "ALL") -> pd.DataFrame:
    """상장 종목 목록 조회. market: 'KOSPI', 'KOSDAQ', 'ALL'"""
    import FinanceDataReader as fdr
    if market == "ALL":
        kospi = fdr.StockListing("KOSPI")[["Code", "Name", "Market"]]
        kosdaq = fdr.StockListing("KOSDAQ")[["Code", "Name", "Market"]]
        return pd.concat([kospi, kosdaq], ignore_index=True)
    return fdr.StockListing(market)[["Code", "Name", "Market"]]


def get_price_history(ticker: str, start: str, end: Optional[str] = None) -> pd.DataFrame:
    """주가 히스토리 조회. start/end: 'YYYY-MM-DD' 형식"""
    import FinanceDataReader as fdr
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")
    return fdr.DataReader(ticker, start, end)


def get_current_price(ticker: str) -> Optional[float]:
    """당일 현재가 조회"""
    from pykrx import stock
    today = datetime.today().strftime("%Y%m%d")
    df = stock.get_market_ohlcv(today, today, ticker)
    if df.empty:
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv(yesterday, yesterday, ticker)
    if df.empty:
        return None
    return float(df["종가"].iloc[-1])


def search_disclosures(corp_code: str, start: str, end: Optional[str] = None) -> list:
    """DART 공시 검색. DART_API_KEY 환경변수 필요. start/end: 'YYYYMMDD'"""
    import os
    import dart_fss as dart
    api_key = os.environ.get("DART_API_KEY")
    if not api_key:
        raise EnvironmentError("DART_API_KEY 환경변수가 설정되지 않았습니다.")
    dart.set_api_key(api_key)
    if end is None:
        end = datetime.today().strftime("%Y%m%d")
    filings = dart.filings.search(corp_code=corp_code, bgn_de=start, end_de=end)
    return filings


if __name__ == "__main__":
    print("=== fetch.py 동작 테스트 ===")
    print("\n[1] 삼성전자 최근 5일 시세")
    end = datetime.today().strftime("%Y%m%d")
    start = (datetime.today() - timedelta(days=7)).strftime("%Y%m%d")
    df = get_ohlcv("005930", start, end)
    print(df.tail())

    print("\n[2] 삼성전자 현재가")
    price = get_current_price("005930")
    print(f"현재가: {price:,.0f}원" if price else "조회 실패")

    print("\n[3] KOSPI 종목 수")
    listing = get_ticker_list("KOSPI")
    print(f"KOSPI 상장 종목 수: {len(listing)}")
```

- [ ] **Step 3: 스크립트 실행 테스트**

```powershell
python "D:\Agents\Stock\scripts\fetch.py"
```

Expected: 삼성전자 시세 DataFrame, 현재가, KOSPI 종목 수 출력 (API 연결 성공)

- [ ] **Step 4: Commit**

```bash
git add scripts\fetch.py
git commit -m "feat: add stock data fetch utilities"
```

---

## Task 10: wiki 동기화 스크립트 (scripts\sync_wiki.py)

**Files:**
- Create: `scripts\sync_wiki.py`

- [ ] **Step 1: sync_wiki.py 작성**

`D:\Agents\Stock\scripts\sync_wiki.py`:

```python
"""portfolio.db → wiki MD 파일 자동 동기화"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "portfolio.db"
WIKI_PATH = Path(__file__).parent.parent / "wiki" / "portfolio"
INITIAL_CASH = 5_000_000.0
TARGET_ASSET = 500_000_000.0


def _get_conn():
    return sqlite3.connect(DB_PATH)


def sync_holdings():
    conn = _get_conn()
    holdings = conn.execute(
        "SELECT ticker, company_name, quantity, avg_price, current_price FROM holdings ORDER BY ticker"
    ).fetchall()
    budget = conn.execute(
        "SELECT cash, total_invested, total_asset FROM budget ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    cash = budget[0] if budget else INITIAL_CASH
    total_invested = budget[1] if budget else 0.0
    total_asset = budget[2] if budget else INITIAL_CASH
    achievement = (total_asset / TARGET_ASSET) * 100

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 보유 종목 현황",
        "",
        "> 이 파일은 `scripts\\sync_wiki.py` 가 자동으로 갱신합니다. 직접 수정하지 마세요.",
        "",
        f"최종 동기화: {ts}",
        "",
        "## 현금",
        "",
        "| 항목 | 금액 |",
        "|---|---|",
        f"| 현금 잔액 | {cash:,.0f}원 |",
        f"| 총 투자금 | {total_invested:,.0f}원 |",
        f"| 총 자산 | {total_asset:,.0f}원 |",
        f"| 목표 대비 달성률 | {achievement:.2f}% |",
        "",
        "## 보유 종목",
        "",
    ]

    if not holdings:
        lines.append("_없음_")
        lines.append("")
        lines.append("| 티커 | 종목명 | 수량 | 평균단가 | 현재가 | 평가금액 | 손익 | 손익률 |")
        lines.append("|---|---|---|---|---|---|---|---|")
    else:
        lines.append("| 티커 | 종목명 | 수량 | 평균단가 | 현재가 | 평가금액 | 손익 | 손익률 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for ticker, name, qty, avg, cur in holdings:
            cur = cur or avg
            value = cur * qty
            pnl = (cur - avg) * qty
            pnl_pct = ((cur - avg) / avg) * 100
            lines.append(
                f"| {ticker} | {name} | {qty:,} | {avg:,.0f}원 | {cur:,.0f}원 | {value:,.0f}원 | {pnl:+,.0f}원 | {pnl_pct:+.2f}% |"
            )

    (WIKI_PATH / "holdings.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] holdings.md 동기화 완료")


def sync_performance():
    conn = _get_conn()
    snapshots = conn.execute(
        "SELECT snapshot_date, total_asset FROM budget ORDER BY snapshot_date"
    ).fetchall()
    conn.close()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest_asset = snapshots[-1][1] if snapshots else INITIAL_CASH
    cumulative_return = ((latest_asset - INITIAL_CASH) / INITIAL_CASH) * 100
    achievement = (latest_asset / TARGET_ASSET) * 100

    lines = [
        "# 수익률 현황",
        "",
        "> 이 파일은 `scripts\\sync_wiki.py` 가 자동으로 갱신합니다.",
        "",
        f"최종 동기화: {ts}",
        "",
        "## 요약",
        "",
        "| 항목 | 수치 |",
        "|---|---|",
        f"| 초기 자산 | {INITIAL_CASH:,.0f}원 |",
        f"| 현재 총 자산 | {latest_asset:,.0f}원 |",
        f"| 누적 수익률 | {cumulative_return:+.2f}% |",
        f"| 목표 금액 | {TARGET_ASSET:,.0f}원 |",
        f"| 목표 달성률 | {achievement:.2f}% |",
        "",
        "## 일별 자산 스냅샷",
        "",
        "| 날짜 | 총 자산 |",
        "|---|---|",
    ]
    for date, asset in snapshots:
        lines.append(f"| {date} | {asset:,.0f}원 |")

    (WIKI_PATH / "performance.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] performance.md 동기화 완료")


def sync_trade_history():
    conn = _get_conn()
    trades = conn.execute(
        "SELECT transaction_date, transaction_type, ticker, company_name, quantity, price, total_amount "
        "FROM transactions ORDER BY transaction_date DESC, id DESC"
    ).fetchall()
    conn.close()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 거래 이력",
        "",
        "> 이 파일은 `scripts\\sync_wiki.py` 가 자동으로 갱신합니다.",
        "",
        f"최종 동기화: {ts}",
        "",
        "| 날짜 | 구분 | 티커 | 종목명 | 수량 | 단가 | 총금액 |",
        "|---|---|---|---|---|---|---|",
    ]
    for date, ttype, ticker, name, qty, price, total in trades:
        label = "매수" if ttype == "BUY" else "매도"
        lines.append(f"| {date} | {label} | {ticker} | {name} | {qty:,} | {price:,.0f}원 | {total:,.0f}원 |")

    if not trades:
        lines.append("| - | - | - | - | - | - | - |")

    (WIKI_PATH / "trade-history.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] trade-history.md 동기화 완료")


def sync_all():
    print(f"=== wiki 동기화 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    sync_holdings()
    sync_performance()
    sync_trade_history()
    print("=== 동기화 완료 ===")


if __name__ == "__main__":
    sync_all()
```

- [ ] **Step 2: 스크립트 실행 테스트**

```powershell
python "D:\Agents\Stock\scripts\sync_wiki.py"
```

Expected output:
```
=== wiki 동기화 시작: 2026-05-29 HH:MM:SS ===
[OK] holdings.md 동기화 완료
[OK] performance.md 동기화 완료
[OK] trade-history.md 동기화 완료
=== 동기화 완료 ===
```

- [ ] **Step 3: 동기화 결과 확인**

```powershell
Get-Content "D:\Agents\Stock\wiki\portfolio\holdings.md"
```

Expected: 현금 5,000,000원, 보유 종목 없음 테이블 출력

- [ ] **Step 4: Commit**

```bash
git add scripts\sync_wiki.py
git commit -m "feat: add wiki sync script (DB -> MD)"
```

---

## Task 11: 최종 검증

- [ ] **Step 1: 전체 파일 구조 확인**

```powershell
Get-ChildItem -Recurse "D:\Agents\Stock" | Where-Object { -not $_.PSIsContainer } | Select-Object FullName
```

Expected: CLAUDE.md, 모든 rules\*.md, 모든 wiki\*.md, data\portfolio.db, scripts\*.py 포함

- [ ] **Step 2: DB 데이터 확인**

```powershell
python -c "
import sqlite3
conn = sqlite3.connect('D:/Agents/Stock/data/portfolio.db')
budget = conn.execute('SELECT * FROM budget').fetchall()
print('Budget:', budget)
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print('Tables:', [t[0] for t in tables])
conn.close()
"
```

Expected: budget 테이블에 초기 5,000,000원 레코드 존재

- [ ] **Step 3: 전체 동기화 재실행**

```powershell
python "D:\Agents\Stock\scripts\sync_wiki.py"
```

Expected: 3개 파일 동기화 완료

- [ ] **Step 4: 최종 커밋**

```bash
git add .
git commit -m "feat: claudebuffett company infrastructure complete"
```

---

## 구현 완료 후 메시 첫 실행

모든 태스크 완료 후, 새 Claude Code 세션에서 `D:\Agents\Stock` 디렉토리를 열면 CLAUDE.md를 읽은 메시가 자동으로:
1. 팀 현황 확인
2. 팀 구성 결정 (축구선수 이름으로 역할 배정)
3. 초기 시장 분석 시작
