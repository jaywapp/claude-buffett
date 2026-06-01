#!/usr/bin/env python3
"""음바페: 스크리닝 데이터 수집기 (2026-06-02)"""
import sys
from datetime import datetime, timedelta
import pandas as pd
from scripts.fetch import get_ohlcv, get_current_price

# 대상 종목 및 매핑
STOCKS = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "042700": "한미반도체",
    "087010": "펩트론",
    "000100": "유한양행",
    "042660": "한화오션",
    "329180": "HD현대중공업",
    "010120": "LS일렉트릭",
    "298040": "효성중공업",
    "105560": "KB금융",
    "012450": "한화에어로스페이스"
}

def get_52w_highs_lows(ticker: str) -> tuple:
    """52주 고점, 저점 조회"""
    try:
        # 과거 1년 데이터 조회
        today = datetime.today()
        one_year_ago = today - timedelta(days=365)
        start_date = one_year_ago.strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")

        df = get_ohlcv(ticker, start_date, end_date)
        if df.empty:
            return None, None

        high_52w = df["고가"].max()
        low_52w = df["저가"].min()
        return float(high_52w), float(low_52w)
    except Exception as e:
        print(f"[ERROR] {ticker} 52주 데이터 조회 실패: {e}", file=sys.stderr)
        return None, None

def get_recent_5_trading_days(ticker: str) -> pd.DataFrame:
    """최근 5거래일 OHLCV 조회"""
    try:
        # 2026-05-26 ~ 2026-05-30 (5거래일)
        df = get_ohlcv(ticker, "20260526", "20260530")
        return df
    except Exception as e:
        print(f"[ERROR] {ticker} 5거래일 데이터 조회 실패: {e}", file=sys.stderr)
        return pd.DataFrame()

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

def main():
    print("[음바페] 스크리닝 데이터 수집 시작...")
    print(f"대상: {len(STOCKS)}개 종목")
    print(f"기준일: 2026-05-29 (최근 거래일)")
    print()

    screening_data = []
    ohlcv_data = {}

    # 1. 각 종목별 데이터 수집
    for ticker, name in STOCKS.items():
        print(f"[{ticker}] {name}...", end=" ", flush=True)
        try:
            # 현재가 조회
            current_price = get_current_price(ticker)

            # 52주 고점/저점 조회
            high_52w, low_52w = get_52w_highs_lows(ticker)

            # 5거래일 OHLCV
            ohlcv_df = get_recent_5_trading_days(ticker)
            ohlcv_data[ticker] = ohlcv_df

            # 최근 거래일 종가 (2026-05-29)
            if not ohlcv_df.empty:
                recent_close = ohlcv_df.iloc[-1]["종가"]
                prev_close = ohlcv_df.iloc[-2]["종가"] if len(ohlcv_df) >= 2 else recent_close
            else:
                recent_close = current_price
                prev_close = current_price

            # 전일대비, 등락률 계산
            diff = recent_close - prev_close if prev_close else 0
            change_rate = (diff / prev_close * 100) if prev_close else 0

            screening_data.append({
                "티커": ticker,
                "종목명": name,
                "현재가": current_price,
                "전일대비": diff,
                "등락률": change_rate,
                "52W고점": high_52w,
                "52W저점": low_52w
            })

            print("✓")
        except Exception as e:
            print(f"✗ (오류: {e})", file=sys.stderr)

    # 2. 마크다운 생성
    md = "# 스크리닝 데이터 — 2026-06-02\n\n"
    md += "수집일: 2026-06-02\n"
    md += "기준가: 2026-05-29 (최근 거래일 종가)\n\n"

    # 3. 요약 테이블
    md += "| 티커 | 종목명 | 현재가 | 전일대비 | 등락률 | 52W고점 | 52W저점 |\n"
    md += "|------|--------|--------|---------|--------|---------|----------|\n"

    for row in screening_data:
        md += f"| {row['티커']} | {row['종목명']} | {format_currency(row['현재가'])} | "
        md += f"{format_currency(row['전일대비'])} | {format_percentage(row['등락률'])} | "
        md += f"{format_currency(row['52W고점'])} | {format_currency(row['52W저점'])} |\n"

    # 4. 5거래일 OHLCV 상세 데이터
    md += "\n## 5거래일 등락 현황\n\n"
    md += "```\n\n"

    for ticker, name in STOCKS.items():
        if ticker in ohlcv_data and not ohlcv_data[ticker].empty:
            df = ohlcv_data[ticker].copy()
            # 등락률 계산
            df['등락률'] = df['종가'].pct_change() * 100

            md += f"[{ticker}] {name}\n"
            # 컬럼명 정리
            df_display = df[['시가', '고가', '저가', '종가', '거래량', '등락률']].copy()
            md += df_display.to_string()
            md += "\n\n"

    md += "```"

    # 5. 파일 저장
    output_file = "D:\\Agents\\Stock\\docs\\screening-2026-06-02.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md)

    print()
    print(f"✓ 저장 완료: {output_file}")
    print(f"✓ 수집된 종목: {len(screening_data)}개")

    return 0

if __name__ == "__main__":
    sys.exit(main())
