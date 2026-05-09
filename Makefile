.PHONY: dev build

VENV := .venv
PELICAN := $(VENV)/bin/pelican

$(PELICAN):
	python -m venv $(VENV)
	$(VENV)/bin/pip install -e .

dev: $(PELICAN)
	$(PELICAN) --autoreload --listen

build: $(PELICAN)
	$(PELICAN) content -o output -s publishconf.py
