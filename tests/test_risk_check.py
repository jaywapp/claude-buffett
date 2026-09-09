import contextlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import risk_check


class RiskTests(unittest.TestCase):
    def test_empty_holdings_and_zero_assets(self):
        self.assertEqual(risk_check.check_risks([], {'total_asset': 100, 'cash': 100, 'total_invested': 0}), [])
        self.assertEqual(len(risk_check.check_risks([], {'total_asset': 0, 'cash': 0})), 1)

    def test_boundaries_price_fallback_and_inactive_holdings(self):
        holding = {'ticker': 'TEST', 'name': 'Test', 'quantity': 1, 'avg_price': 100, 'current_price': None}
        budget = {'total_asset': 500, 'cash': 50, 'total_invested': 100}
        self.assertEqual(risk_check.check_risks([holding], budget), [])
        self.assertEqual(risk_check.check_risks([dict(holding, quantity=0)], dict(budget, total_invested=0)), [])
        warnings = risk_check.check_risks([dict(holding, current_price=80)], dict(budget, cash=49))
        self.assertEqual(len(warnings), 3)
        self.assertIn('현금', warnings[0])
        self.assertIn('개별', warnings[1])
        self.assertIn('총 포트폴리오', warnings[2])

    def test_missing_database_does_not_create_file(self):
        with tempfile.TemporaryDirectory() as folder:
            missing = Path(folder) / 'missing.db'
            with patch.object(risk_check, 'DB_PATH', missing), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(risk_check.main(), 1)
            self.assertFalse(missing.exists())

    def test_connection_failure_is_reported(self):
        with patch.object(Path, 'exists', return_value=True), patch.object(sqlite3, 'connect', side_effect=sqlite3.OperationalError), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(risk_check.main(), 1)
        self.assertIn('OperationalError', output.getvalue())

    def test_schema_failure_returns_failure_and_closes_connection(self):
        connection = sqlite3.connect(':memory:')
        with patch.object(risk_check, 'connect_db', return_value=connection), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(risk_check.main(), 1)
        self.assertIn('DB 조회 실패', output.getvalue())
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute('SELECT 1')

    def test_empty_budget_is_explicit_failure(self):
        connection = sqlite3.connect(':memory:')
        connection.execute('CREATE TABLE holdings (ticker, company_name, quantity, avg_price, current_price)')
        connection.execute('CREATE TABLE budget (cash, total_invested, total_asset, snapshot_date)')
        with patch.object(risk_check, 'connect_db', return_value=connection), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(risk_check.main(), 1)


if __name__ == '__main__':
    unittest.main()
