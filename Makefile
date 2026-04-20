.PHONY: dev build

VENV := .venv
PELICAN := $(VENV)/bin/pelican

dev:
	$(PELICAN) --autoreload --listen

build:
	$(PELICAN) content -o output -s publishconf.py
