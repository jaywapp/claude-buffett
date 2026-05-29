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
