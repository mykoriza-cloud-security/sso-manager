"""
Module to manage SSO groups
"""
import os
from http import HTTPStatus
from botocore.config import Config

import boto3
from pydantic import ValidationError
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    CORSConfig,
    Response,
    content_types,
)
from aws_lambda_powertools.utilities.idempotency import (
    DynamoDBPersistenceLayer,
    IdempotencyConfig,
    idempotent,
)

# Env vars
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
CORS_MAX_AGE = os.getenv("CORS_MAX_AGE", 300)
CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")
CORS_EXTRA_ORIGINS = os.getenv("CORS_EXTRA_ORIGINS", [])
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", [])
CORS_EXPOSE_HEADERS = os.getenv("CORS_EXPOSE_HEADERS", [])
IDENTITY_STORE_ID = os.getenv("IDENTITY_STORE_ID", "d-1234567890")
DDB_TABLE_NAME = os.getenv("TABLE_NAME", "cloud_pass")
IDEMPOTENCY_DDB_TABLE_NAME = os.getenv("TABLE_NAME", "cloud_pass_idempotency_store")
TRACER_SERVICE_NAME = os.getenv("TRACER_SERVICE_NAME", "regex_rules_microservice")

# AWS Lambda powertool objects & class instances
tracer = Tracer(service=TRACER_SERVICE_NAME)
logger = Logger(service=TRACER_SERVICE_NAME, level="INFO")
cors_config = CORSConfig(
    allow_origin=CORS_ALLOW_ORIGIN,
    extra_origins=CORS_EXTRA_ORIGINS,
    max_age=CORS_MAX_AGE,
    allow_headers=CORS_ALLOW_HEADERS,
    expose_headers=CORS_EXPOSE_HEADERS,
)
app = APIGatewayRestResolver(enable_validation=True, cors=cors_config)
idempotency_ddb = DynamoDBPersistenceLayer(IDEMPOTENCY_DDB_TABLE_NAME)
idempotency_config = IdempotencyConfig(
    event_key_jmespath="[requestContext.authorizer.user_id, body]",
)
config = Config(
    region_name=AWS_REGION,
    connect_timeout=1,
    retries={"total_max_attempts": 2, "max_attempts": 5},
)


# Lambda Routes
@app.exception_handler(ValidationError)
def incorrect_input_dataype(exc: ValidationError):
    """
    Handle invalid request parameters
    """
    metadata = {
        "path": app.current_event.path,
        "query_strings": app.current_event.query_string_parameters,
        "body": app.current_event.body,
    }
    logger.error(f"Malformed request: {exc}", extra=metadata)
    return Response(
        status_code=HTTPStatus.BAD_REQUEST.value,
        content_type=content_types.TEXT_PLAIN,
        body=HTTPStatus.BAD_REQUEST.phrase,
    )


@app.not_found()
@tracer.capture_method
def handle_not_found_errors(exc: NotFoundError) -> Response:  # pylint: disable=W0613
    """
    Lambda function route to handle unknown routes
    """
    logger.info(f"Route: {app.current_event.path} Not found")
    return Response(
        status_code=HTTPStatus.NOT_FOUND.value,
        content_type=content_types.TEXT_PLAIN,
        body=HTTPStatus.NOT_FOUND.phrase,
    )


@app.get("/")
def health_check():
    """
    Lambda function route to handle health checks
    """
    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=HTTPStatus.OK.phrase,
    )


@app.get("/sso/groups")
@tracer.capture_method
def get_sso_groups():
    """
    Get list of SSO groups
    """
    identity_store_client = boto3.client("identitystore")
    extracted_query_string_params = (
        app.current_event._data.query_string_parameters  # pylint: disable=W0212
    )
    query_string_params = (
        extracted_query_string_params if extracted_query_string_params else {}
    )

    modified_kwargs = {}
    next_token = query_string_params.get("next_token", "")
    max_results = query_string_params.get("max_results", 25)

    kwargs = {
        "IdentityStoreId": IDENTITY_STORE_ID,
        "MaxResults": max_results,
        "NextToken": next_token,
    }

    for k in kwargs:
        if kwargs[k]:
            modified_kwargs[k] = kwargs[k]

    identitystore_client_response = identity_store_client.list_groups(**modified_kwargs)
    sso_groups, next_token = identitystore_client_response.get(
        "Groups", []
    ), identitystore_client_response.get("NextToken", "")

    for i, group in enumerate(sso_groups):
        if "IdentityStoreId" in group.keys():
            sso_groups[i].pop(
                "IdentityStoreId"
            )  # Identity store IDs are globally unique. Must be obfuscated for security reasons

    sso_groups_server_response = {"sso_groups": sso_groups, "next_token": next_token}

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=sso_groups_server_response,
    )


# Lambda handler
@tracer.capture_lambda_handler
@event_source(data_class=APIGatewayProxyEvent)  # pylint: disable=E1120
@logger.inject_lambda_context(
    log_event=False,
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
)
@idempotent(  # pylint: disable=E1120
    persistence_store=idempotency_ddb, config=idempotency_config
)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Function to create permission sets.

    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
    is_regex: string
        Boolean value indicating whether string is a valid regex or not
    """
    return app.resolve(event, context)
