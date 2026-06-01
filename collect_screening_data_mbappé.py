#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""음바페: 스크리닝 데이터 수집 (2026-06-02)"""

import sys
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# 대상 종목 매핑 (ticker -> name)
STOCKS = {
    "005930.KS": ("삼성전자", "005930"),
    "000660.KS": ("SK하이닉스", "000660"),
    "042700.KS": ("한미반도체", "042700"),
    "087010.KS": ("펩트론", "087010"),
    "000100.KS": ("유한양행", "000100"),
    "042660.KS": ("한화오션", "042660"),
    "329180.KS": ("HD현대중공업", "329180"),
    "010120.KS": ("LS일렉트릭", "010120"),
    "298040.KS": ("효성중공업", "298040"),
    "105560.KS": ("KB금융", "105560"),
    "012450.KS": ("한화에어로스페이스", "012450"),
}

def format_currency(value):
    """금액 포맷"""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{int(value):,}"

def format_percentage(value):
    """백분율 포맷"""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.2f}%"

def get_stock_data(ticker_yf, ticker_short):
    """yfinance를 사용해 종목 데이터 조회"""
    try:
        # 1년 데이터 조회
        stock = yf.Ticker(ticker_yf)

        # 1년 히스토리
        one_year_ago = datetime.now() - timedelta(days=365)
        df_1y = stock.history(start=one_year_ago.strftime("%Y-%m-%d"), end=datetime.now().strftime("%Y-%m-%d"))

        if df_1y.empty:
            return None

        # 5거래일 데이터 (최근 5일)
        df_5d = df_1y.tail(5).copy()

        # 현재가 (최근 종가)
        current_price = float(df_1y['Close'].iloc[-1])

        # 52주 고점/저점
        high_52w = float(df_1y['High'].max())
        low_52w = float(df_1y['Low'].min())

        return {
            "current_price": current_price,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "df_5d": df_5d,
        }
    except Exception as e:
        print(f"  [오류] {ticker_short}: {str(e)}", file=sys.stderr)
        return None

def main():
    print("=" * 80)
    print("스크리닝 데이터 수집 중... (2026-06-02)")
    print("기준가: 2026-05-29 (금요일 종가 - 최근 거래일)")
    print(f"대상 종목 수: {len(STOCKS)}")
    print("=" * 80)
    print()

    results = []
    errors = []

    for ticker_yf, (name, ticker_short) in STOCKS.items():
        print(f"[{ticker_short}] {name}...", end="", flush=True)
        try:
            data = get_stock_data(ticker_yf, ticker_short)
            if data is None:
                raise ValueError("데이터 조회 실패")

            results.append({
                "ticker": ticker_short,
                "ticker_yf": ticker_yf,
                "name": name,
                "current_price": data["current_price"],
                "high_52w": data["high_52w"],
                "low_52w": data["low_52w"],
                "df_5d": data["df_5d"],
            })
            print(" OK")

        except Exception as e:
            error_msg = f"{ticker_short}: {str(e)}"
            errors.append(error_msg)
            print(f" FAIL")

    # 보고서 생성
    report = generate_report(results, errors)

    # 파일 저장
    output_path = r"D:\Agents\Stock\docs\screening-2026-06-02.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print()
    print("=" * 80)
    print(f"저장됨: {output_path}")
    print(f"수집된 종목: {len(results)}개")
    print("=" * 80)

    return 0 if not errors else 1

def generate_report(results, errors):
    """마크다운 보고서 생성"""

    lines = [
        "# 스크리닝 데이터 — 2026-06-02",
        "",
        "수집일: 2026-06-02",
        "기준가: 2026-05-29 (최근 거래일 종가)",
        "",
        "| 티커 | 종목명 | 현재가 | 52W고점 | 52W저점 |",
        "|------|--------|--------|---------|---------|",
    ]

    # 테이블 행
    for result in results:
        ticker = result["ticker"]
        name = result["name"]
        price = format_currency(result["current_price"])
        high_52w = format_currency(result["high_52w"])
        low_52w = format_currency(result["low_52w"])
        lines.append(f"| {ticker} | {name} | {price} | {high_52w} | {low_52w} |")

    # 5거래일 등락 현황
    lines.append("")
    lines.append("## 5거래일 OHLCV")
    lines.append("")
    lines.append("```")

    for result in results:
        ticker = result["ticker"]
        name = result["name"]
        df = result["df_5d"].copy()

        lines.append(f"\n[{ticker}] {name}")
        if df is not None and not df.empty:
            # 영문 컬럼명을 한문으로 변환
            df_display = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df_display.columns = ['시가', '고가', '저가', '종가', '거래량']

            # 인덱스를 날짜 형식으로 변환 (YYYY-MM-DD)
            df_display.index = df_display.index.strftime('%Y-%m-%d')

            # 숫자를 정수로 변환
            for col in df_display.columns:
                df_display[col] = df_display[col].astype(int)

            lines.append(df_display.to_string())
        else:
            lines.append("데이터 없음")

    lines.append("\n```")

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
