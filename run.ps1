Write-Host "Starting AI Resume Analyzer & Job Recommender..." -ForegroundColor Cyan
Set-Location -Path $PSScriptRoot
& "$PSScriptRoot\.venv\Scripts\python.exe" -m streamlit run "$PSScriptRoot\app.py"
