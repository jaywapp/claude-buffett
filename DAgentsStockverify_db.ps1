Add-Type -AssemblyName System.Data.SQLite -ErrorAction SilentlyContinue
$connStr = 'Data Source=D:\Agents\Stock\data\portfolio.db;Version=3'
$conn = New-Object System.Data.SQLite.SQLiteConnection $connStr
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT name FROM sqlite_master WHERE type='table'"
$reader = $cmd.ExecuteReader()
$tables = @()
while ($reader.Read()) { $tables += $reader[0] }
$reader.Close()
Write-Host "Tables: $($tables -join ', ')"

$cmd.CommandText = 'SELECT cash, total_invested, total_asset FROM budget'
$reader = $cmd.ExecuteReader()
while ($reader.Read()) { Write-Host "Budget: cash=$($reader[0]), total_invested=$($reader[1]), total_asset=$($reader[2])" }
$reader.Close()

$conn.Close()
