PYTHON ?= python3
ARGS ?=

.PHONY: run test check-scripts

run:
	PYTHONPATH=src $(PYTHON) -m shell_emulator $(ARGS)

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

check-scripts:
	for script in scripts/*.sh; do sh $$script || exit 1; done
