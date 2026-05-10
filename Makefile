.PHONY: dev devbuild build

VENV := .venv
PELICAN := $(VENV)/bin/pelican

$(PELICAN):
	python -m venv $(VENV)
	$(VENV)/bin/pip install -e .

dev: $(PELICAN)
	$(PELICAN) --autoreload --listen

devbuild: $(PELICAN)
	$(PELICAN) content

build: $(PELICAN)
	$(PELICAN) content -o output -s publishconf.py
