"""Unit tests to test querying regex rules from DDB"""

# Imports
import json
import decimal
import pathlib
import unittest
from http import HTTPStatus

import moto
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

# Local package imports
from cloud_pass.ddb import DDB
from cloud_pass.utils import generate_lambda_context, create_table, delete_table
from src.lambdas.regex_rules.app.index import lambda_handler
from .utils import COMMON_ERROR_MESSAGES

# Globals
DDB_TABLE_NAME = "cloud_pass"
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()


@moto.mock_dynamodb
class TestGetRegexRules(unittest.TestCase):
    """Class to test querying regex rules from DDB"""

    def setUp(self) -> None:
        """Creates DDB table, writes sample data to DDB table, and
        lambda context prior to test case execution
        """
        self._py_ddb = DDB(DDB_TABLE_NAME)
        self._lambda_context = generate_lambda_context()
        self._expected_keys = ["pk", "sk", "priority", "regex"]
        create_table(DDB_TABLE_NAME)
        self._write_to_table()

    def tearDown(self) -> None:
        """Delete DDB table after test case execution"""
        delete_table(DDB_TABLE_NAME)

    def _write_to_table(self) -> None:
        """Writes mock data to DynamoDB table"""
        self._ddb_items = [
            {
                "pk": "RGX_RULES",
                "sk": "RGX_01HF5GJM3C5DVC3A2R01J4959Z",
                "priority": decimal.Decimal(0),
                "regex": r"\d+(\.\d\d)?",
            },
            {
                "pk": "RGX_RULES",
                "sk": "RGX_01HF5GMZ4WHVEZAFZT6F71VC1G",
                "priority": decimal.Decimal(1),
                "regex": r"[^i*&2@]",
            },
            {
                "pk": "RGX_RULES",
                "sk": "RGX_01HF5GN552ERSEH92WVRSR3GXQ",
                "priority": decimal.Decimal(2),
                "regex": r"//[^\r\n]*[\r\n]",
            },
        ]
        self._py_ddb.batch_put_items(self._ddb_items)

    ##############################################
    #        Test Cases - lambda handler         #
    ##############################################

    def test_lambda_handler_no_event_body(self) -> None:
        """Test case to query all regex rules

        Operation:
            - GET /rules/regex with no event body

        Asserts:
            - HTTP status code is 200
            - Expected returned regex rules list length is 3
            - DDB Item secondary key follows desired regex pattern of "RGX_([a-zA-Z0-9]{26})"
            - DDB Item primary key name is RGX_RULES
            - DDB Item numerical attributes are float datatype
            - DDB Item contains expected item attributes
        """
        # Arrange
        apigw_event = APIGatewayProxyEvent(
            data={
                "path": "/rules/regex",
                "httpMethod": "GET",
                "requestContext": {"requestId": "227b78aa-779d-47d4-a48e-ce62120393b8"},
            }
        )
        # Act
        response = lambda_handler(apigw_event, self._lambda_context)
        response_body = json.loads(response["body"])

        # Assert
        self.assertEqual(response["statusCode"], HTTPStatus.OK.value)
        self.assertEqual(
            len(response_body), len(self._ddb_items), COMMON_ERROR_MESSAGES["list_size"]
        )
        for item in response_body:
            self.assertEqual(item["pk"], "RGX_RULES", COMMON_ERROR_MESSAGES["hash_key"])
            self.assertIsInstance(
                item["priority"], float, COMMON_ERROR_MESSAGES["ddb_numerical"]
            )
            self.assertCountEqual(
                self._expected_keys,
                list(item.keys()),
                COMMON_ERROR_MESSAGES["expected_keys"],
            )
            self.assertRegex(
                item["sk"],
                r"RGX_([a-zA-Z0-9]{26})",
                COMMON_ERROR_MESSAGES["regex_pattern"],
            )

    def test_lambda_handler_empty_event_body(self) -> None:
        """Test case to query all regex rules

        Operation:
            - GET /rules/regex with empty event body

        Asserts:
            - HTTP status code is 200
            - Expected returned regex rules list length is 3
            - DDB Item secondary key follows desired regex pattern of "RGX_([a-zA-Z0-9]{26})"
            - DDB Item primary key name is RGX_RULES
            - DDB Item numerical attributes are float datatype
            - DDB Item contains expected item attributes
        """
        # Arrange
        apigw_event = APIGatewayProxyEvent(
            data={
                "body": {},
                "path": "/rules/regex",
                "httpMethod": "GET",
                "requestContext": {"requestId": "227b78aa-779d-47d4-a48e-ce62120393b8"},
            }
        )

        # Act
        response = lambda_handler(apigw_event, self._lambda_context)
        response_body = json.loads(response["body"])

        # Assert
        self.assertEqual(response["statusCode"], HTTPStatus.OK.value)
        self.assertEqual(
            len(response_body), len(self._ddb_items), COMMON_ERROR_MESSAGES["list_size"]
        )
        for item in response_body:
            self.assertEqual(item["pk"], "RGX_RULES", COMMON_ERROR_MESSAGES["hash_key"])
            self.assertIsInstance(
                item["priority"], float, COMMON_ERROR_MESSAGES["ddb_numerical"]
            )
            self.assertCountEqual(
                self._expected_keys,
                list(item.keys()),
                COMMON_ERROR_MESSAGES["expected_keys"],
            )
            self.assertRegex(
                item["sk"],
                r"RGX_([a-zA-Z0-9]{26})",
                COMMON_ERROR_MESSAGES["regex_pattern"],
            )
