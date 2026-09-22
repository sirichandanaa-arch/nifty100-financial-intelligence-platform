.PHONY: install load ratios test report dashboard api clean all final
install:
	python -m pip install -r requirements.txt
load:
	python -m src.etl.loader
ratios:
	python -m src.analytics.ratios
screener:
	python -m src.screener.engine
report:
	python -m src.reports.generate_all
cluster:
	python -m src.analytics.clustering
api-spec:
	python -m src.api.export_openapi
all:
	python -m src.pipeline

test:
	pytest tests/ --html=reports/pytest_report.html --self-contained-html -q
final:
	python -m src.finalize

dashboard:
	streamlit run src/dashboard/app.py
api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000
clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
