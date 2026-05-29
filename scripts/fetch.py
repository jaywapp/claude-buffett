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
