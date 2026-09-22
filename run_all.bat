@echo off
call .venv\Scripts\activate
python -m src.pipeline
pytest tests --html=reports\pytest_report.html --self-contained-html -q
python -m src.acceptance
python -m src.finalize
pause
