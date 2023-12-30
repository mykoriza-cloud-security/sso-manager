"""
Unit test module to test non functional routes such as health checks &
route not found scenarios
"""

# Imports
import json
import unittest
from http import HTTPStatus

import moto
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

# Local package imports
from src.app.index import lambda_handler
from src.app.lib.utils import generate_lambda_context


class TestNonFunctionalRoutes(unittest.TestCase):
    """
    Test cases to test non functional routes such as health checks &
    route not found scenarios
    """

    def setUp(self) -> None:
        """
        Create DDB table and lambda context prior to test case execution
        """
        self._lambda_context = generate_lambda_context()

    def test_lambda_handler_health_check(self) -> None:
        """
        Test case for health check

        Operation:
            Sends HTTP GET request to healthcheck route

        Asserts:
            - HTTP status code is 200
            - HTTP response body is: "Health check!"
        """
        # Arrange
        apigw_event = APIGatewayProxyEvent(
            data={
                "path": "/",
                "httpMethod": "GET",
            }
        )

        # Act
        response = lambda_handler(apigw_event, self._lambda_context)

        # Assert
        self.assertEqual(response["statusCode"], HTTPStatus.OK.value)
        self.assertEqual(json.loads(response["body"]), HTTPStatus.OK.phrase)

    def test_lambda_handler_route_not_found_wrong_path(self) -> None:
        """
        Test case for non-existant HTTP route

        Operation:
            Sends HTTP requests to an unknown route

        Asserts:
            - HTTP status code is 404
            - HTTP response body is: "Route not found!"
        """
        http_methods = ["GET", "PUT", "POST", "DELETE"]

        for method in http_methods:
            # Arrange
            apigw_event = APIGatewayProxyEvent(
                data={
                    "body": {},
                    "path": "/not_found",  # Path doesn't exist
                    "httpMethod": method,
                }
            )

            # Act
            response = lambda_handler(apigw_event, self._lambda_context)

            # Assert
            self.assertEqual(response["body"], HTTPStatus.NOT_FOUND.phrase)
            self.assertEqual(response["statusCode"], HTTPStatus.NOT_FOUND.value)

    def test_lambda_handler_route_not_found_wrong_http_method(self) -> None:
        """
        Test case for non-existant HTTP route

        Operation:
            Sends HTTP requests to an unknown route

        Asserts:
            - HTTP status code is 404
            - HTTP response body is: "Route not found!"
        """
        http_methods = [
            "PUT",
            "POST",
            "DELETE",
        ]  # GET not part of the list due to healthcheck route

        for method in http_methods:
            # Arrange
            apigw_event = APIGatewayProxyEvent(
                data={
                    "body": {},
                    "path": "/",  # Path exists
                    "httpMethod": method,
                }
            )

            # Act
            response = lambda_handler(apigw_event, self._lambda_context)

            # Assert
            self.assertEqual(response["body"], HTTPStatus.NOT_FOUND.phrase)
            self.assertEqual(response["statusCode"], HTTPStatus.NOT_FOUND.value)
