"""
Unit tests to test writing regex rules from DDB
"""

# Imports
import importlib
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent
from src.app.lib.utils import generate_lambda_context


def test() -> None:
    # Arrange
    from src.app import index
    importlib.reload(index)
    context = generate_lambda_context()
    
    # Act
    lambda_response = index.lambda_handler(EventBridgeEvent(data={}), context)

    # # Act
    # event = EventBridgeEvent(data={})
    # response = lambda_handler(event, context)
    # assert response == True
