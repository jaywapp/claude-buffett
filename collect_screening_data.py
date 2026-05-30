#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""스크리닝 데이터 수집 스크립트 (음바페)"""

import re
import sys
from datetime import datetime, timedelta
import traceback
from pathlib import Path

try:
    import FinanceDataReader as fdr
    import pandas as pd
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)


# coverage.md에서 티커 목록을 동적으로 로드
COVERAGE_PATH = Path("D:/Agents/Stock/wiki/company/coverage.md")


def load_tickers_from_coverage(path: Path) -> list[tuple[str, str]]:
    """coverage.md 파일에서 (ticker, name) 목록을 파싱한다.

    테이블 형식: | 기업명 | 티커 | 시장 | 섹터 | 등록일 |
    """
    if not path.exists():
        print(f"[경고] coverage.md 파일을 찾을 수 없습니다: {path}")
        return []

    tickers = []
    # 헤더/구분선 행은 건너뛰고, 데이터 행만 파싱
    row_pattern = re.compile(
        r"^\|\s*(?P<name>[^|]+?)\s*\|\s*(?P<ticker>\d{6})\s*\|"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        m = row_pattern.match(line)
        if m:
            tickers.append((m.group("ticker"), m.group("name")))
    return tickers


# 오늘 날짜(수집일) 및 기준일(전날) 자동 계산
COLLECTION_DATE = datetime.today().strftime("%Y-%m-%d")
REFERENCE_DATE = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

# 동적 티커 목록 (coverage.md 기준)
TICKERS = load_tickers_from_coverage(COVERAGE_PATH)


def get_ticker_data(ticker):
    """종목 데이터 조회"""
    try:
        # 1년 데이터 조회
        end_date = datetime.strptime(REFERENCE_DATE, "%Y-%m-%d")
        start_date = end_date - timedelta(days=365)

        df = fdr.DataReader(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        if df.empty:
            return None

        # 최신 데이터 (기준일)
        latest = df.iloc[-1]
        current_price = float(latest["Close"])

        # 52주 범위
        high_52w = float(df["High"].max())
        low_52w = float(df["Low"].min())

        # 최근 5거래일
        ohlcv_5d = df.tail(5).copy()

        return {
            "current_price": current_price,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "ohlcv_5d": ohlcv_5d,
        }
    except Exception as e:
        print(f"[오류] {ticker}: {str(e)}")
        traceback.print_exc()
        return None


def main():
    print("=" * 80)
    print(f"스크리닝 데이터 수집 중... ({COLLECTION_DATE})")
    print(f"기준가: {REFERENCE_DATE} 종가")
    print(f"대상 종목 수: {len(TICKERS)}")
    print("=" * 80 + "\n")

    if not TICKERS:
        print("[오류] 로드된 종목이 없습니다. coverage.md를 확인하세요.")
        return 1

    results = []
    errors = []

    for ticker, name in TICKERS:
        print(f"[{ticker}] {name}...", end="", flush=True)
        try:
            data = get_ticker_data(ticker)
            if data is None:
                raise ValueError("데이터 조회 실패")

            results.append({
                "ticker": ticker,
                "name": name,
                "current_price": data["current_price"],
                "high_52w": data["high_52w"],
                "low_52w": data["low_52w"],
                "ohlcv_5d": data["ohlcv_5d"],
            })
            print(" OK")

        except Exception as e:
            error_msg = f"{ticker}: {str(e)}"
            errors.append(error_msg)
            print(f" FAIL")

    # 보고서 생성
    report = generate_report(results, errors)

    # 파일 저장
    output_path = Path("D:/Agents/Stock/docs") / f"screening-{COLLECTION_DATE}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n{'=' * 80}")
    print(f"저장됨: {output_path}")
    print(f"{'=' * 80}")

    return 0 if not errors else 1


def generate_report(results, errors):
    """마크다운 보고서 생성"""

    # 테이블 헤더
    lines = [
        f"# 스크리닝 데이터 — {COLLECTION_DATE}",
        "",
        f"수집일: {COLLECTION_DATE}",
        f"기준가: {REFERENCE_DATE} 종가",
        "",
        "| 티커 | 종목명 | 현재가 | 52W고점 | 52W저점 |",
        "|------|--------|--------|---------|---------|",
    ]

    # 테이블 행
    for result in results:
        ticker = result["ticker"]
        name = result["name"]
        price = f"{result['current_price']:,.0f}" if result['current_price'] else "-"
        high_52w = f"{result['high_52w']:,.0f}" if result['high_52w'] else "-"
        low_52w = f"{result['low_52w']:,.0f}" if result['low_52w'] else "-"

        lines.append(f"| {ticker} | {name} | {price} | {high_52w} | {low_52w} |")

    # 5거래일 등락 현황
    lines.append("")
    lines.append("## 5거래일 등락 현황")
    lines.append("")
    lines.append("```")
    for result in results:
        ticker = result["ticker"]
        name = result["name"]
        ohlcv = result["ohlcv_5d"]

        lines.append(f"\n[{ticker}] {name}")
        if ohlcv is not None and not ohlcv.empty:
            lines.append(ohlcv.to_string())
        else:
            lines.append("데이터 없음")

    lines.append("```")

    # 오류 로그
    if errors:
        lines.append("")
        lines.append("## 수집 오류")
        lines.append("")
        lines.append("```")
        for error in errors:
            lines.append(error)
        lines.append("```")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
