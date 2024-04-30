# """
# Unit tests to test querying regex rules from DDB
# """

# Imports
import os
import pytest
from src.app.lib.aws_dynamodb import DDB

def test_missing_constructor_parameter() -> None:
    # Arrange
    with pytest.raises(TypeError):
        DDB()

def test_list_implicit_assignment_rules(setup_dynamodb: pytest.fixture):

    # Arrange
    ddb_table_name = os.getenv("DDB_TABLE_NAME")
    py_ddb = DDB(ddb_table_name)

    # Act
    quried_rules = py_ddb.batch_query_items(key = "IMPLICIT", range_begins_with="IMPLICIT_")

    # Assert
    assert len(quried_rules) == len(setup_dynamodb["rbac_definitions"])
    for rule in quried_rules:
        assert rule["rule_type"] == "REGEX"
