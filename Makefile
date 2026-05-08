.PHONY: dev build lint

VENV := .venv
PELICAN := $(VENV)/bin/pelican

$(PELICAN):
	python -m venv $(VENV)
	$(VENV)/bin/pip install -e .

dev: $(PELICAN)
	$(PELICAN) --autoreload --listen

lint: $(PELICAN)
	$(VENV)/bin/python -m frontmatter_lint content

build: $(PELICAN)
	$(PELICAN) content -o output -s publishconf.py
