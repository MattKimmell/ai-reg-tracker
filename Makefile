.PHONY: static seed run

static:
	python scripts/export_static.py

seed:
	python scripts/seed_baseline.py

run:
	uvicorn app.main:app --host 127.0.0.1 --port 8765
