import pytest
from src.app.lib.utils import generate_lambda_context

@pytest.fixture(autouse=True)
def set_aws_creds(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "test")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    yield

@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("DDB_TABLE_NAME", "cloud_pass")
    monkeypatch.setenv("IDENTITY_STORE_ID", "d-1234567890")
    monkeypatch.setenv("IDENTITY_STORE_ARN", "arn:aws:sso:::instance/ssoins-instanceId")
    yield

@pytest.fixture(autouse=True)
def context():
    return generate_lambda_context()
