@echo off
echo Starting AI Resume Analyzer & Job Recommender...
cd /d "%~dp0"
call .venv\Scripts\python.exe -m streamlit run app.py
pause
