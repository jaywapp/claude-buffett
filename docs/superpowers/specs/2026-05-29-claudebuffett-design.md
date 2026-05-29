# 클로드버핏 — 시스템 설계 스펙

**작성일:** 2026-05-29  
**상태:** 승인됨

---

## 1. 개요

AI로만 구성된 가상 주식투자회사 **클로드버핏**을 구축한다.  
초기 예산 500만 원을 5억 원으로 불리는 것이 최종 목표이며, 국내주식(레버리지·인버스 제외)만 대상으로 한다.

---

## 2. 폴더 구조

```
D:\Agents\Stock\
├── prompts\
│   └── start.md
├── rules\
│   ├── agents\
│   │   ├── messi.md              # 대표 메시 역할·권한·행동 규칙
│   │   └── [팀원이름].md         # 각 팀원 역할 규칙 (메시가 고용 시 생성)
│   ├── investment.md             # 투자 원칙, 리스크 한도, 종목 선정 기준
│   ├── communication.md          # 에이전트 간 보고 체계 및 에스컬레이션
│   ├── reporting.md              # 보고서 형식·주기 규칙
│   └── tools.md                  # Codex 플러그인 활용 가이드
├── wiki\
│   ├── company\
│   │   ├── org-chart.md
│   │   └── team.md
│   ├── portfolio\
│   │   ├── holdings.md           # 보유 종목 현황 (DB 자동 동기화)
│   │   ├── performance.md        # 수익률 요약
│   │   └── trade-history.md      # 거래 이력
│   ├── market\
│   │   ├── watchlist.md
│   │   └── analysis\             # 종목별 분석 페이지
│   └── strategy\
│       └── investment-thesis.md  # 투자 철학·전략
├── docs\                         # 작업용 임시 문서
├── report\
│   ├── daily\
│   └── weekly\
└── data\
    └── portfolio.db              # SQLite 원장
```

---

## 3. 에이전트 아키텍처

### 3.1 메시 (대표, 오케스트레이터)
- **모델:** Claude Sonnet
- **역할:** 사용자와 직접 소통, 시장 상황 자율 판단, 팀원 spawn/해고, 최종 투자 결정
- **동작:** `Agent` 툴로 서브에이전트를 동적 생성 → 결과 수합 → 판단 → 실행

### 3.2 팀원 구성 원칙
- **메시가 첫 가동 시 팀 구성 전원 결정** (역할·이름·모델 모두 메시 주도)
- 팀원 이름은 축구선수명 사용
- 각 팀원은 `rules\agents\[이름].md` 참조하여 동작
- 모델 배분 원칙:

| 역할 유형 | 권장 모델 | 이유 |
|---|---|---|
| 리서치·분석·판단·보고서 | Claude Sonnet | 자연어 추론, 뉴스·공시 해석, 문서 작성 |
| 데이터 수집·코드 실행·DB 작업 | Codex | 반복적 코드 실행, API 호출, 자동화 |

### 3.3 자율 운영 사이클
```
메시 (자율 판단)
  ↓ spawn
  ├── 리서치팀  → 종목 스크리닝 (pykrx / FinanceDataReader)
  ├── 분석팀   → 기술적·기본적 분석
  ├── 리스크팀  → 포지션 사이징·리스크 평가
  ↓ 결과 수합 → 투자 결정
  ├── portfolio.db 업데이트 (Codex)
  ├── wiki\portfolio\ MD 동기화 (Codex)
  └── report\ 보고서 생성
```

---

## 4. 데이터 레이어

### 4.1 공개 API 스택
| 라이브러리 | 용도 |
|---|---|
| `pykrx` | OHLCV 시세, 거래량, 시가총액 |
| `FinanceDataReader` | 재무제표, 주가 히스토리 |
| `dart-fss` | DART 공시 (실적, 이벤트) |
| `requests` + 네이버금융 | 뉴스, 업종 동향 |

### 4.2 SQLite 스키마 (portfolio.db)
```sql
holdings      -- 보유 종목 (ticker, 수량, 평균단가, 현재가)
transactions  -- 거래 이력 (매수/매도, 날짜, 수량, 가격)
watchlist     -- 관심 종목
budget        -- 잔액 및 총 자산 스냅샷
```

### 4.3 wiki 자동 동기화
DB 변경 시 Codex 에이전트가 자동으로:
- `wiki\portfolio\holdings.md` 갱신
- `wiki\portfolio\performance.md` 갱신
- `wiki\portfolio\trade-history.md` 갱신

### 4.4 리스크 규칙
- 단일 종목 최대 비중: 총 자산의 20%
- 레버리지·인버스 전면 금지
- 손절 기준: -15% 도달 시 리스크팀 자동 경고

---

## 5. Rules 구조 및 커뮤니케이션

### 5.1 rules\ 파일 요약
| 파일 | 핵심 내용 |
|---|---|
| `rules\agents\messi.md` | 대표 행동 원칙, 의사결정 권한, 팀 고용/해고 기준, 사용자 소통 방식 |
| `rules\agents\[팀원].md` | 역할 정의, 사용 툴, 결과물 형식, 보고 대상 |
| `rules\investment.md` | 종목 선정 기준, 리스크 한도, 투자 철학 |
| `rules\communication.md` | 에이전트 간 보고 체계, 에스컬레이션 조건 |
| `rules\reporting.md` | 보고서 템플릿, 저장 경로, 주기 |
| `rules\tools.md` | Codex 플러그인 활용 가이드 |

### 5.2 Codex 활용 원칙
Codex 플러그인을 **기본 실행 도구**로 지정. 다음 작업은 Codex 우선:
- API 호출 및 데이터 수집
- SQLite CRUD 작업
- wiki MD 자동 생성·갱신
- 보고서 수치 계산 및 포맷팅
- 반복 가능한 모든 코드 작업

Claude = 판단·해석·작성 / Codex = 실행·자동화 (역할 명확 분리)

### 5.3 커뮤니케이션 흐름
```
사용자
  ↕
메시 (대표, Claude Sonnet)
  ├─ 지시 → 팀원 (Claude/Codex 서브에이전트)
  ├─ 결과 수합 → 판단
  └─ 보고 → 사용자 / report\
```

---

## 6. 예산 및 목표
- **초기 예산:** 5,000,000원
- **목표:** 500,000,000원 (100배)
- **투자 대상:** 국내주식 (코스피·코스닥)
- **제외 종목:** 레버리지, 인버스, 기타 파생 ETF
