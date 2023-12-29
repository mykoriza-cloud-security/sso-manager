"""
Unit tests to test writing regex rules from DDB
"""

# Imports
import json
import pathlib
import decimal
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
IDEMPOTENCY_DDB_TABLE_NAME = "cloud_pass_idempotency_store"
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()


@moto.mock_dynamodb
class TestPutRegexRules(unittest.TestCase):
    """
    Class to test writing regex rules to DDB
    """

    def setUp(self) -> None:
        """
        Creates DDB table, writes sample data to DDB table, and
        lambda context prior to test case execution
        """
        self._py_ddb = DDB(DDB_TABLE_NAME)
        self._expected_keys = ["pk", "sk", "priority", "regex"]
        self._lambda_context = generate_lambda_context()
        create_table(table_name=DDB_TABLE_NAME, primary_key="pk", secondary_key="sk")
        create_table(table_name=IDEMPOTENCY_DDB_TABLE_NAME, primary_key="id")

    def tearDown(self) -> None:
        """
        Delete DDB table after test case execution
        """
        delete_table(DDB_TABLE_NAME)
        delete_table(IDEMPOTENCY_DDB_TABLE_NAME)

    # def test_lambda_handler_no_event_body(self) -> None:
    #     """
    #     Test case to write regex rules

    #     Operation:
    #         - PUT /rules/regex

    #     Asserts:
    #         - HTTP status code is 200
    #         - HTTP response body is: "No input provided"
    #         - Expected returned regex rules list length is 0
    #     """
    #     # Arrange
    #     apigw_event = APIGatewayProxyEvent(
    #         data={"httpMethod": "PUT", "path": "/rules/regex"}
    #     )

    #     # Act
    #     response = lambda_handler(apigw_event, self._lambda_context)
    #     stored_rules = self._py_ddb.batch_query_items(
    #         key="RGX_RULES", range_begins_with="RGX_"
    #     )

    #     # Assert
    #     self.assertEqual(json.loads(response["body"]), HTTPStatus.NO_CONTENT.phrase)
    #     self.assertEqual(response["statusCode"], HTTPStatus.NO_CONTENT.value)
    #     self.assertEqual(len(stored_rules), 0, COMMON_ERROR_MESSAGES["list_size"])

    # def test_lambda_handler_empty_event_body(self) -> None:
    #     """
    #     Test case to write regex rules with empty event body

    #     Operation:
    #         - PUT /rules/regex with empty event body

    #     Asserts:
    #         - HTTP status code is 200
    #         - HTTP response body is: "No input provided"
    #         - Expected returned regex rules list length is 0
    #     """
    #     # Arrange
    #     apigw_event = APIGatewayProxyEvent(
    #         data={"body": {}, "httpMethod": "PUT", "path": "/rules/regex"}
    #     )

    #     # Act
    #     response = lambda_handler(apigw_event, self._lambda_context)
    #     stored_rules = self._py_ddb.batch_query_items(
    #         key="RGX_RULES", range_begins_with="RGX_"
    #     )

    #     # Assert
    #     self.assertEqual(json.loads(response["body"]), HTTPStatus.NO_CONTENT.phrase)
    #     self.assertEqual(response["statusCode"], HTTPStatus.NO_CONTENT.value)
    #     self.assertEqual(len(stored_rules), 0, COMMON_ERROR_MESSAGES["list_size"])

    # def test_lambda_handler_empty_regex_rules(self) -> None:
    #     """
    #     Test case to write regex rules with event body
    #     containing no regex rules

    #     Operation:
    #         - PUT /rules/regex

    #     Asserts:
    #         - HTTP status code is 200
    #         - HTTP response body is: "No input provided"
    #         - Expected returned regex rules list length is 0
    #     """
    #     # Arrange
    #     apigw_event = APIGatewayProxyEvent(
    #         data={
    #             "httpMethod": "PUT",
    #             "path": "/rules/regex",
    #             "body": {"regex_rules": []},
    #         }
    #     )

    #     # Act
    #     response = lambda_handler(apigw_event, self._lambda_context)
    #     stored_rules = self._py_ddb.batch_query_items(
    #         key="RGX_RULES", range_begins_with="RGX_"
    #     )

    #     # Assert
    #     self.assertEqual(json.loads(response["body"]), HTTPStatus.NO_CONTENT.phrase)
    #     self.assertEqual(response["statusCode"], HTTPStatus.NO_CONTENT.value)
    #     self.assertEqual(len(stored_rules), 0, COMMON_ERROR_MESSAGES["list_size"])

    # def test_lambda_handler_eighty_safe_regex_rules(self) -> None:
    #     """
    #     Test case to write regex rules with event body of 80
    #     safe regex rules

    #     Operation:
    #         - PUT /rules/regex with event bodies containing 80
    #             safe regex rules

    #     Asserts:
    #         - HTTP status code is 200
    #         - HTTP response body is: "Batch write successul"
    #         - Expected returned regex rules list length is 80
    #         - DDB Item secondary key follows desired regex pattern of "RGX_([a-zA-Z0-9]{26})"
    #         - DDB Item primary key name is RGX_RULES
    #         - DDB Item numerical attributes are decimal.Decimal datatype
    #         - DDB Item contains expected item attributes
    #     """
    #     # Arrange
    #     with open(
    #         f"{CURRENT_DIR}/events/eighty_safe_regex_rules.json", encoding="utf-8"
    #     ) as fp:
    #         apigw_event = json.load(fp)
    #         apigw_event = APIGatewayProxyEvent(data=apigw_event)

    #     # Act
    #     response = lambda_handler(apigw_event, self._lambda_context)
    #     queried_regexes = self._py_ddb.batch_query_items(
    #         key="RGX_RULES", range_begins_with="RGX_"
    #     )

    #     # Assert
    #     self.assertEqual(len(queried_regexes), 80, COMMON_ERROR_MESSAGES["list_size"])
    #     self.assertEqual(response["statusCode"], HTTPStatus.OK.value)
    #     self.assertEqual(
    #         json.loads(response["body"]),
    #         HTTPStatus.OK.phrase,
    #     )
    #     for item in queried_regexes:
    #         self.assertEqual(item["pk"], "RGX_RULES", COMMON_ERROR_MESSAGES["hash_key"])
    #         self.assertRegex(
    #             item["sk"],
    #             r"RGX_([a-zA-Z0-9]{26})",
    #             COMMON_ERROR_MESSAGES["regex_pattern"],
    #         )
    #         self.assertIsInstance(
    #             item["priority"],
    #             decimal.Decimal,
    #             COMMON_ERROR_MESSAGES["ddb_numerical"],
    #         )
    #         self.assertCountEqual(
    #             self._expected_keys,
    #             list(item.keys()),
    #             COMMON_ERROR_MESSAGES["expected_keys"],
    #         )

    # def test_lambda_handler_incorrect_input_datatype(self) -> None:
    #     """
    #     Test case to test error handling of incorrect datatypes

    #     Operation:
    #         - PUT /rules/regex with different event bodies containing
    #             incorrect datatypes

    #     Asserts:
    #         - HTTP status code is 400
    #         - HTTP response body is: "Invalid request parameters"
    #         - Expected returned regex rules list length is 0
    #         - DDB Item secondary key follows desired regex pattern of "RGX_([a-zA-Z0-9]{26})"
    #         - DDB Item primary key name is RGX_RULES
    #         - DDB Item numerical attributes are decimal.Decimal datatype
    #         - DDB Item contains expected item attributes
    #     """
    #     sample_inputs = [
    #         [{}, {}, {}],
    #         [1, 2, 3],
    #         [{"test_1": "1", "test_2": "2"}],
    #         "test",
    #     ]
    #     for input_ in sample_inputs:
    #         # Arrange
    #         apigw_event_contents = {
    #             "body": {"regex_rules": input_},
    #             "path": "/rules/regex",
    #             "httpMethod": "PUT",
    #             "requestContext": {"requestId": "227b78aa-779d-47d4-a48e-ce62120393b8"},
    #         }
    #         apigw_event = APIGatewayProxyEvent(apigw_event_contents)

    #         # Act
    #         response = lambda_handler(apigw_event, self._lambda_context)
    #         stored_rules = self._py_ddb.batch_query_items(
    #             key="RGX_RULES", range_begins_with="RGX_"
    #         )

    #         # Assert
    #         self.assertEqual(response["body"], HTTPStatus.BAD_REQUEST.phrase)
    #         self.assertEqual(response["statusCode"], HTTPStatus.BAD_REQUEST.value)
    #         self.assertEqual(len(stored_rules), 0, COMMON_ERROR_MESSAGES["list_size"])

    # def test_lambda_handler_idempotency(self) -> None:
    #     """
    #     Test case to test idempotency of lambda handler

    #     Operation:
    #         - PUT /rules/regex with different event bodies containing
    #             80 safe regex rules

    #     Asserts:
    #         -
    #     """
    #     # Arrange
    #     identity_id = "b4a34c56-7890-4ab6-123c-567890def012"
    #     regex_rules = [
    #         "^[a-zA-Z0-9]+$",
    #         "^\\d{2}-\\d{2}-\\d{4}$",
    #         "^[\\w.%+-]+@[\\w.-]+\\.[a-zA-Z]{2,}$",
    #     ]
    #     apigw_event_contents = {
    #         "httpMethod": "PUT",
    #         "path": "/rules/regex",
    #         "body": {"regex_rules": regex_rules},
    #         "requestContext": {"authorizer": {"user_id": identity_id}},
    #     }
    #     apigw_event = APIGatewayProxyEvent(data=apigw_event_contents)

    #     # Act
    #     for _ in range(0, 3):
    #         lambda_handler(apigw_event, self._lambda_context)

    #     queried_regexes = self._py_ddb.batch_query_items(
    #         key="RGX_RULES", range_begins_with="RGX_"
    #     )

    #     # Assert
    #     self.assertEqual(
    #         len(queried_regexes), len(regex_rules), COMMON_ERROR_MESSAGES["list_size"]
    #     )
