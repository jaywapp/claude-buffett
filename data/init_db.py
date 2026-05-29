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
