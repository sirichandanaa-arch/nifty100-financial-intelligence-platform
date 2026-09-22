# Nifty 100 Analytics — Build Instructions

1. Activate `.venv`.
2. Install `requirements.txt`.
3. Put the 12 supplied Excel files in `source/`.
4. Run `python -m src.pipeline`.
5. Run `pytest tests/ --html=reports/pytest_report.html --self-contained-html -q`.
6. Run `python -m src.acceptance`.
7. Run `python -m src.finalize`.

On Windows, `make` is optional; the Python commands above are the canonical cross-platform commands.
