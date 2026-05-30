#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""스크리닝 데이터 수집 스크립트 (음바페)"""

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


# 대상 종목 정의
TICKERS = [
    ("005930", "삼성전자"),
    ("000660", "SK하이닉스"),
    ("042700", "한미반도체"),
    ("087010", "펩트론"),
    ("000100", "유한양행"),
    ("042660", "한화오션"),
    ("329180", "HD현대중공업"),
    ("010120", "LS ELECTRIC"),
    ("298040", "효성중공업"),
    ("105560", "KB금융"),
]

COLLECTION_DATE = "2026-05-30"
REFERENCE_DATE = "2026-05-29"  # 금요일


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
    print("=" * 80 + "\n")

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
        f"기준가: {REFERENCE_DATE} (금요일 종가)",
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
