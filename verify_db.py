import sqlite3

conn = sqlite3.connect('D:/Agents/Stock/data/portfolio.db')
try:
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print('Tables:', [t[0] for t in tables])
    budget = conn.execute('SELECT cash, total_invested, total_asset FROM budget').fetchall()
    print('Budget:', budget)
finally:
    conn.close()
