# Define your environment and command options
PYTHON = python3
LINTER = black ruff mypy
TEST_DIRS = tests/functional tests/unit tests/integration

# Helper to log with timestamp
log_with_date = echo "\n[$(shell date '+%Y-%m-%d %H:%M:%S')]\n"

# Install pip-tools, compile all .in files to .txt files, and install dependencies
reqs:
	$(call log_with_date) "Activating virtualenv and installing dependencies..." >> .logs/reqs_log.txt 2>&1
	rm -rf .venv && \
	${PYTHON} -m venv .venv && \
	source .venv/bin/activate && \
	$(PYTHON) -m pip install pip-tools && \
	$(PYTHON) -m piptools compile requirements.in && \
	$(PYTHON) -m piptools compile requirements_dev.in && \
	$(PYTHON) -m piptools compile requirements_test.in >> .logs/reqs_log.txt 2>&1

sync: reqs
	$(call log_with_date) "Syncing requirements..." >> .logs/sync_log.txt 2>&1
	$(PYTHON) -m piptools sync requirements*.txt >> .logs/sync_log.txt 2>&1

install: reqs
	$(call log_with_date) "Installing development and test dependencies..." >> .logs/install_log.txt 2>&1
	$(PYTHON) -m pip install -r requirements.txt && \
	$(PYTHON) -m pip install -r requirements_dev.txt && \
	$(PYTHON) -m pip install -r requirements_test.txt >> .logs/install_log.txt 2>&1

lint:
	$(call log_with_date) "Running linters (black, ruff, mypy, safety)..." >> .logs/lint_log.txt 2>&1
	echo "mypy" >> .logs/lint_log.txt 2>&1
	$(PYTHON) -m mypy . >> .logs/lint_log.txt 2>&1 || true
	echo "black" >> .logs/lint_log.txt 2>&1
	$(PYTHON) -m black --check . >> .logs/lint_log.txt 2>&1 || true
	echo "ruff" >> .logs/lint_log.txt 2>&1
	ruff check . >> .logs/lint_log.txt 2>&1 || true
	safety check -r requirements.txt >> .logs/lint_log.txt 2>&1 || true

# Tests command to run pytest tests under functional and unit directories
tests:
	$(call log_with_date) "Running tests under functional and unit directories..." >> .logs/test_log.txt 2>&1
	$(PYTHON) -m pytest $(TEST_DIRS) >> .logs/test_log.txt 2>&1

# 'all' command to run reqs, install, lint, and tests in sequence
all: reqs install lint tests
	@echo "All tasks (reqs, install, lint, tests) completed."

.PHONY: lint tests reqs all
