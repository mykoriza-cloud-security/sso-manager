.ONESHELL:

.PHONY: unittest format

# Environment Setup
env:
	@echo "Creating Python virtual environment"
	@python3 -m venv .venv

	@echo "Activating virtual environment"
	@. .venv/bin/activate

	@echo "Upgrading pip3"
	@pip3 install --upgrade pip

	@echo "Installing dependencies"
	@pip3 install -r requirements.txt

# Automated Testing
unittest:
	@echo "Running unit tests"
	@pytest -s -v

# Formatting & Linting
format:
	@echo "Running python formatting"
	@black ./src/

	@echo "Running python linter"
	@pylint ./src/

# Remove cached python folders
cleanup:
	@echo "Remove Python Debris"
	@pyclean . --debris --verbose
