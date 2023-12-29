"""
Module to test querying SSO group lambda
"""
import json
import unittest
from http import HTTPStatus

import moto
import boto3
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

# Local package imports
from cloud_pass.utils import generate_lambda_context
from src.lambdas.sso_groups.app.index import lambda_handler


@moto.mock_identitystore
@moto.mock_secretsmanager
class TestListSsoGroups(unittest.TestCase):
    """
    Unit test cases to test querying SSO group lambda
    """

    def setUp(self) -> None:
        """
        Initialize idenitity store ID variable, generate lambda
        context & initialize AWS boto3 clients
        """
        self._identity_store_id = "d-1234567890"
        self._lambda_context = generate_lambda_context()
        self._identity_store_client = boto3.client("identitystore")
        self._secretsmanager_client = boto3.client("secretsmanager")

    def _create_sso_groups(self, num_of_groups: int) -> None:
        """
        Method to create IAM Identity Center SSO groups

        Parameters
        ----------
            - num_of_groups: int, required
                Number of SSO groups to create
        """
        for i in range(0, num_of_groups):
            self._identity_store_client.create_group(
                IdentityStoreId=self._identity_store_id, DisplayName=f"GROUP_{i}"
            )

    # def test_identity_store_id_removed(self) -> None:
    #     """
    #     Test case to check if IdentityStoreId is not in response. Identity
    #     store IDs are globally unique. Therefore, for security purposes
    #     this ID must be obfuscated to prevent it being visible in a server-client
    #     response and used in an SSO based attack
    #     """

    #     # Arrange
    #     self._create_sso_groups(30)
    #     apigw_event = APIGatewayProxyEvent(
    #         data={
    #             "path": "/sso/groups",
    #             "httpMethod": "GET",
    #             "requestContext": {"requestId": "227b78aa-779d-47d4-a48e-ce62120393b8"},
    #         }
    #     )

    #     # Act
    #     response = lambda_handler(apigw_event, self._lambda_context)
    #     response_body = json.loads(response["body"])
    #     sso_groups = response_body["sso_groups"]

    #     # Assert
    #     self.assertEqual(response["statusCode"], HTTPStatus.OK.value)
    #     for group in sso_groups:
    #         self.assertNotIn(
    #             "IdentityStoreId",
    #             group.keys(),
    #             "Security - Identity Store ID must be obfuscated from response",
    #         )

    # def test_maximum_page_size(self) -> None:
    #     """
    #     Test adjustment of page size or queried SSO groups via
    #     query string parameters
    #     """

    #     # Arrange
    #     page_size = 5
    #     self._create_sso_groups(30)
    #     apigw_event = APIGatewayProxyEvent(
    #         data={
    #             "path": "/sso/groups",
    #             "httpMethod": "GET",
    #             "requestContext": {"requestId": "227b78aa-779d-47d4-a48e-ce62120393b8"},
    #             "queryStringParameters": {"max_results": 5},
    #         }
    #     )

    #     # Act
    #     response = lambda_handler(apigw_event, self._lambda_context)
    #     response_body = json.loads(response["body"])
    #     sso_groups = response_body["sso_groups"]

    #     # Assert
    #     self.assertIn("next_token", response_body)
    #     self.assertLessEqual(page_size, len(sso_groups))
    #     self.assertEqual(response["statusCode"], HTTPStatus.OK.value)

    # def test_pagination(self) -> None:
    #     """
    #     Test adjustment of page size or queried SSO groups via
    #     query string parameters
    #     """

    #     # Arrange
    #     page_size = 5
    #     next_token = ""
    #     num_of_pages = 6
    #     current_page = 1
    #     self._create_sso_groups(30)

    #     while True:
    #         apigw_event = APIGatewayProxyEvent(
    #             data={
    #                 "path": "/sso/groups",
    #                 "httpMethod": "GET",
    #                 "requestContext": {
    #                     "requestId": "227b78aa-779d-47d4-a48e-ce62120393b8"
    #                 },
    #                 "queryStringParameters": {
    #                     "max_results": page_size,
    #                     "next_token": next_token,
    #                 },
    #             }
    #         )

    #         # Act
    #         response = lambda_handler(apigw_event, self._lambda_context)
    #         response_body = json.loads(response["body"])

    #         # Assert
    #         next_token = response_body["next_token"]
    #         if not next_token:
    #             break
    #         current_page += 1

    #     self.assertEqual(current_page, num_of_pages)
    #     self.assertEqual(response["statusCode"], HTTPStatus.OK.value)
