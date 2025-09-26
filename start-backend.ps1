# -------------------------------
# 1️⃣ Activate virtual environment
$venvPath = ".\backend\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    . $venvPath
} else {
    Write-Host "Virtual environment not found. Run: python -m venv .venv" -ForegroundColor Red
    exit
}

# -------------------------------
# 2️⃣ Set PYTHONPATH to backend
$env:PYTHONPATH="$PWD\backend"

# -------------------------------
# 3️⃣ Run Uvicorn backend
python run.py

# command to run: .\start-backend.ps1