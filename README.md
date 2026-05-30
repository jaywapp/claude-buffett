# Claude Buffett

Claude AI를 활용한 주식 투자 분석 시스템입니다. 종목 분석, 초록 데이터 해석, 시장 동향 리포트를 자동으로 작성합니다.

## 보고서 뷰어

**[버핏 리포트 웹뷰어 →](https://jaywapp.github.io/claude-buffett/)**

모바일·PC 어디서나 보고서를 열람할 수 있습니다.

## 보고서 종류

| 폴더 | 설명 |
|------|------|
| `report/request/` | 특정 종목·이슈에 대한 요청 분석 보고서 |
| `report/daily/` | 일간 시장 동향 보고서 |
| `report/weekly/` | 주간 포트폴리오 리뷰 보고서 |

## 보고서 추가 방법

`report/{daily|weekly|request}/` 폴더에 마크다운 파일을 추가하면 웹뷰어에 자동으로 반영됩니다.

```
report/request/YYYY-MM-DD-종목명.md
report/daily/YYYY-MM-DD-일간리뷰.md
report/weekly/YYYY-MM-DD-주간리뷰.md
```

## 프로젝트 구조

```
claude-buffett/
├── report/          # 분석 보고서
│   ├── request/     # 요청 보고서
│   ├── daily/       # 일간 보고서
│   └── weekly/      # 주간 보고서
├── data/            # 원본 데이터
├── prompts/         # Claude 프롬프트
├── scripts/         # 분석 스크립트
└── index.html       # 웹뷰어 (GitHub Pages)
```
