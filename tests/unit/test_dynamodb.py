"""
Unit tests to test querying regex rules from DDB
"""

# Imports
import os
import json
import ulid
import moto
import boto3
import pytest

# Local package imports
from src.app.lib.aws_dynamodb import DDB
from .utils import create_table, delete_table

################################################
#                   Fixtures                   #
################################################


@pytest.fixture(autouse=True)
def get_assignment_rules() -> dict:
    cwd = os.path.dirname(os.path.realpath(__file__))
    organizations_map_path = os.path.join(cwd, "aws_assignment_rules.json")
    with open(organizations_map_path, "r") as fp:
        return json.load(fp)


@pytest.fixture(autouse=True)
def dynamodb_client():
    """
    Fixture to mock DynamoDB
    """
    with moto.mock_dynamodb():
        yield boto3.resource("dynamodb")


@pytest.fixture(autouse=True)
def setup_ddb_table(get_assignment_rules: dict, dynamodb_client: boto3.resource):
    """
    Fixture to create DynamoDB table
    """
    ddb_table_name = os.getenv("DDB_TABLE_NAME")
    create_table(table_name=ddb_table_name, primary_key="pk", secondary_key="sk")
    
    # Write data to table
    ddb_table = boto3.resource("dynamodb").Table(ddb_table_name)
    for item in get_assignment_rules["rbac_definitions"]:
        item["sk"] = f"{item['pk']}_{str(ulid.new())}"
        ddb_table.put_item(Item=item)


################################################
#                     Tests                    #
################################################


def test_missing_constructor_parameter() -> None:
    # Arrange
    with pytest.raises(TypeError):
        DDB()


def test_list_implicit_assignment_rules(get_assignment_rules: dict, dynamodb_client: boto3.resource):

    # Arrange
    ddb_table_name = os.getenv("DDB_TABLE_NAME")
    py_ddb = DDB(ddb_table_name)

    # Act
    quried_rules = py_ddb.batch_query_items(key = "IMPLICIT", range_begins_with="IMPLICIT_")

    # Assert
    assert len(quried_rules) == len(get_assignment_rules["rbac_definitions"])
    for rule in quried_rules:
        assert rule["rule_type"] == "REGEX"
