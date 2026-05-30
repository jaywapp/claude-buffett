#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""카시야스 리스크 점검 스크립트

포트폴리오 리스크를 점검하고 경고 조건 충족 시 exit code 1로 종료한다.

점검 항목 (카시야스 rules 기준):
  1. 단일 종목 비중 > 20%
  2. 현금 비중 < 10%
  3. 개별 종목 손실 > -15%
  4. 총 평가손실 > -20%
  5. 코스피 ±3% 급변 -스킵 (fetch.py 의존, 별도 실행 필요)
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path("D:/Agents/Stock/data/portfolio.db")


def connect_db() -> sqlite3.Connection | None:
    """DB 연결. 파일이 없으면 None 반환."""
    if not DB_PATH.exists():
        print(f"[경고] DB 파일을 찾을 수 없습니다: {DB_PATH}")
        return None
    return sqlite3.connect(DB_PATH)


def fetch_holdings(conn: sqlite3.Connection) -> list[dict]:
    """holdings 테이블 전체 조회."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ticker, company_name, quantity, avg_price, current_price FROM holdings"
    )
    rows = cursor.fetchall()
    return [
        {
            "ticker": r[0],
            "name": r[1],
            "quantity": r[2],
            "avg_price": r[3],
            "current_price": r[4],
        }
        for r in rows
    ]


def fetch_budget(conn: sqlite3.Connection) -> dict | None:
    """budget 테이블 최신 행 조회."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cash, total_invested, total_asset FROM budget ORDER BY snapshot_date DESC LIMIT 1"
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {"cash": row[0], "total_invested": row[1], "total_asset": row[2]}


def check_risks(holdings: list[dict], budget: dict) -> list[str]:
    """리스크 점검 후 경고 메시지 목록 반환."""
    warnings: list[str] = []

    total_asset = budget["total_asset"]
    cash = budget["cash"]

    # 총 자산이 0이면 계산 불가
    if total_asset <= 0:
        warnings.append("[오류] 총 자산이 0 또는 음수 -리스크 계산 불가")
        return warnings

    # --- 조건 2: 현금 비중 < 10% ---
    cash_ratio = cash / total_asset * 100
    if cash_ratio < 10.0:
        warnings.append(
            f"[경고] 현금 비중 부족: {cash_ratio:.1f}% (기준: 10% 이상)"
        )

    # 종목별 평가금액 기준 총 투자금 계산
    total_eval = sum(
        (h["current_price"] or h["avg_price"]) * h["quantity"]
        for h in holdings
        if h["quantity"] > 0
    )

    for h in holdings:
        qty = h["quantity"]
        if qty <= 0:
            continue

        price = h["current_price"] if h["current_price"] else h["avg_price"]
        eval_amount = price * qty
        cost_amount = h["avg_price"] * qty

        # --- 조건 1: 단일 종목 비중 > 20% ---
        if total_asset > 0:
            position_ratio = eval_amount / total_asset * 100
            if position_ratio > 20.0:
                warnings.append(
                    f"[경고] 단일 종목 비중 초과: {h['name']} ({h['ticker']}) "
                    f"{position_ratio:.1f}% (기준: 20% 이하)"
                )

        # --- 조건 3: 개별 종목 손실 > -15% ---
        if cost_amount > 0:
            pnl_ratio = (eval_amount - cost_amount) / cost_amount * 100
            if pnl_ratio <= -15.0:
                warnings.append(
                    f"[경고] 개별 종목 손절 기준 도달: {h['name']} ({h['ticker']}) "
                    f"{pnl_ratio:.1f}% (기준: -15% 이상)"
                )

    # --- 조건 4: 총 평가손실 > -20% ---
    if budget["total_invested"] > 0:
        total_cost = budget["total_invested"]
        total_pnl_ratio = (total_eval - total_cost) / total_cost * 100
        if total_pnl_ratio <= -20.0:
            warnings.append(
                f"[경고] 총 포트폴리오 손실 초과: {total_pnl_ratio:.1f}% (기준: -20% 이상)"
            )

    # --- 조건 5: 코스피 ±3% 급변 -스킵 ---
    # fetch.py의 get_ohlcv를 사용해야 하므로 별도 실행 필요

    return warnings


def main() -> int:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("=" * 60)
    print(f"카시야스 리스크 점검 ({now_str})")
    print("=" * 60)

    conn = connect_db()
    if conn is None:
        print("[종료] DB 연결 실패 -리스크 점검 불가")
        return 1

    try:
        holdings = fetch_holdings(conn)
        budget = fetch_budget(conn)
    finally:
        conn.close()

    if budget is None:
        print("[경고] budget 테이블이 비어 있습니다 -리스크 점검 불가")
        return 1

    if not holdings:
        print("[안내] 보유 종목 없음 -포지션 리스크 해당 없음")

    warnings = check_risks(holdings, budget)

    # 결과 출력
    print()
    if warnings:
        print("## 카시야스 보고")
        print(f"**점검 일시:** {now_str}")

        # 등급 판정
        grade = "높음" if len(warnings) >= 3 else ("보통" if len(warnings) >= 1 else "낮음")
        print(f"**포트폴리오 리스크 등급:** {grade}")
        print(f"**경고 항목:**")
        for w in warnings:
            print(f"  {w}")
        print(f"**권고 조치:** 경고 항목을 확인하고 메시(대표)에게 보고하세요.")
        return 1
    else:
        print("## 카시야스 보고")
        print(f"**점검 일시:** {now_str}")
        print("**포트폴리오 리스크 등급:** 낮음")
        print("**경고 항목:** 없음")
        print("**권고 조치:** 이상 없음")
        return 0


if __name__ == "__main__":
    sys.exit(main())
