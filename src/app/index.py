"""
Regex based rules engine for processing regex input for the
purpose of assiging permission sets.
"""
import os
from http import HTTPStatus

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    Response,
    content_types,
)

# Local package & layer imports
from .lib.ddb import DDB
from .lib.sso import SSO


# Env vars
DDB_TABLE_NAME = os.getenv("TABLE_NAME", "cloud_pass")
IDENTITY_STORE_ID = os.getenv("IDENTITY_STORE_ID", "d-1234567890")
IDENTITY_STORE_ARN = os.getenv("IDENTITY_STORE_ARN", "arn:aws:sso:::instance/ssoins-instanceId")
TRACER_SERVICE_NAME = os.getenv("TRACER_SERVICE_NAME", "regex_rules_microservice")

# AWS Lambda powertool objects & class instances
tracer = Tracer(service=TRACER_SERVICE_NAME)
logger = Logger(service=TRACER_SERVICE_NAME, level="INFO")
app = APIGatewayRestResolver(enable_validation=True, cors=cors_config)
cp_ddb = DDB(DDB_TABLE_NAME)
cp_sso = SSO(IDENTITY_STORE_ID, IDENTITY_STORE_ARN)

# Lambda Routes
@app.put("/sso/assignment")
@tracer.capture_method
def put_rbac_sso_assignments():
    """
    Lambda function route to create RBAC permission set
    Assignments.
    """

    sso_groups = cp_sso.get_sso_groups()
    permission_sets = cp_sso.get_permission_sets()
    # assignment_rules = cp_ddb.batch_query_items()

    print("permission_sets")
    print(permission_sets)


# Lambda handler
@tracer.capture_lambda_handler
@event_source(data_class=APIGatewayProxyEvent)  # pylint: disable=E1120
@logger.inject_lambda_context(
    log_event=False,
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Function to create or retrieve regex rules for SSO permission
    set assignments

    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
    response: dict
        - body: contains stringified response of lambda function
        - statusCode: contains HTTP status code
    """
    return app.resolve(event, context)
