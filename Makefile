# Define your environment and command options
PYTHON = python3
LINTER = black ruff mypy
TEST_DIRS = tests/functional tests/unit tests/integration

# Install pip-tools, compile all .in files to .txt files, and install dependencies
reqs:
	echo "Activating virtualenv and installing dependencies..." > .logs/reqs_log.txt 2>&1
	rm -rf .venv && \
	${PYTHON} -m venv .venv && \
	source .venv/bin/activate && \
	$(PYTHON) -m pip install pip-tools && \
	$(PYTHON) -m piptools compile requirements_dev.in && \
	$(PYTHON) -m piptools compile requirements_test.in > .logs/reqs_log.txt 2>&1


sync:reqs
	$(PYTHON) -m piptools sync requirements*.txt > .logs/sync_log.txt 2>&1

install: reqs
	@echo "Installing development and tests dependencies"
	$(PYTHON) -m pip install -r requirements_dev.txt  && \
	$(PYTHON) -m pip install -r requirements_test.txt > .logs/install_log.txt 2>&1

lint:
	echo "Running linters (black, ruff, mypy)..."
	echo "mypy" > .logs/lint_log.txt 2>&1 || true
	$(PYTHON) -m mypy . > .logs/lint_log.txt 2>&1 || true
	echo "black" > .logs/lint_log.txt 2>&1 || true
	$(PYTHON) -m black --check . > .logs/lint_log.txt 2>&1 || true
	echo "ruff" > .logs/lint_log.txt 2>&1 || true
	ruff check . > .logs/lint_log.txt 2>&1 || true

# Tests command to run pytest tests under functional and unit directories
tests:
	@echo "Running tests under functional and unit directories..."
	$(PYTHON) -m pytest $(TEST_DIRS) > .logs/test_log.txt 2>&1

# 'all' command to run reqs, lint, and tests in sequence
all: reqs install lint tests
	@echo "All tasks (reqs, install, lint, tests) completed."

# Additional useful Makefile commands
# You can add other targets here as needed, e.g., install, clean, etc.

.PHONY: lint tests reqs all