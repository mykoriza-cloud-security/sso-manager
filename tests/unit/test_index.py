"""
Unit tests to test writing regex rules from DDB
"""

# Imports
import os
import importlib
import pytest
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent
from src.app.lib.utils import generate_lambda_context


def test(
    setup_aws_organization: pytest.fixture,
    setup_identity_store: pytest.fixture,
    setup_dynamodb: pytest.fixture
) -> None:
    
    # Arrange
    root_ou_id = setup_aws_organization["root_ou_id"]
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ROOT_OU_ID", root_ou_id)

    from src.app import index
    importlib.reload(index)
    context = generate_lambda_context()
    
    # Act
    lambda_response = index.lambda_handler(EventBridgeEvent(data={}), context)
    print(lambda_response)

    # Assert