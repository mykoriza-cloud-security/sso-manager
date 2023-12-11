.ONESHELL:

.PHONY: unittest lint deploy

# Environment Setup
env:
	@echo "Creating Python virtual environment"
	@python3 -m venv .venv

	@echo "Activating virtual environment"
	@. .venv/bin/activate

bootstrap: env
	@echo "Installing dependencies"
	@pip3 install -r requirements.txt

	@echo "Packaging & installing local lambda layers"
	@python3 -m pip install --editable ./src/layers/python

# Automated Testing
unittest: bootstrap
	@echo "Create .aws directory"
	@mkdir ~/.aws || true

	@echo "Setting place AWS region for moto"
	@echo "[default] \nregion=ca-central-1"

	@echo "Setting placeholder AWS credentials for moto"
	@echo "[default] \naws_access_key_id = 123 \naws_secret_access_key = ABC" > ~/.aws/credentials

	@echo "Running unit tests"
	@export AWS_DEFAULT_REGION=us-east-1
	@python3 -m unittest discover -p 'test_*.py' -v

local-unittest:
	@echo "Running unit tests"
	@python3 -m unittest discover -p 'test_*.py' -v

# Formatting & Linting
format:
	@echo "Running python formatting"
	@black ./src/

lint: format
	@echo "Running python linter"
	@pylint ./src/

	@echo "Running CFN linter"
	@cfn-lint ./cfn/templates/*.yaml

# Deployments
package:
	@echo "Packging CloudFormation templates"
	@mkdir ./cfn/templates/build | true
	@aws cloudformation package \
		--s3-bucket $$BUCKET \
		--template-file ./cfn/templates/main.yaml \
		--force-upload \
		--output-template-file ./cfn/templates/build/main.yaml > /dev/null;

deploy: package
	@echo "Deploying CloudFormation templates"
	@aws cloudformation deploy \
		--template-file ./cfn/templates/build/main.yaml \
		--stack-name cloud-pass \
		--s3-bucket $$BUCKET \
		--force-upload \
		--parameter-overrides file://cfn/params/main.json \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

# Cleanup
	@echo "Remove Python Debris"
	@pyclean . --debris --verbose