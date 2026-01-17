PYTHONPATH := .
export PYTHONPATH

.PHONY: install live cache viz-cache

install:
	python -m pip install -r requirements.txt

live:
	python -m viz.viz_live

cache:
	python -m core.run_and_cache

viz-cache:
	python -m viz.viz_cached
