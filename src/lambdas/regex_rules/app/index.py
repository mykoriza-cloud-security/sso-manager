"""Regex based rules engine for processing regex input for the
purpose of assiging permission sets.
"""
import os
from http import HTTPStatus

import ulid
from pydantic import ValidationError
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.data_classes import (
    event_source,
    APIGatewayProxyEvent,
)
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.event_handler import (
    Response,
    CORSConfig,
    content_types,
    APIGatewayRestResolver,
)

# Local package & layer imports
from cloud_pass.ddb import DDB
from cloud_pass.utils import recursive_process_dict

from .schemas import RegexRulesModel

# Env vars
CORS_MAX_AGE = os.getenv("CORS_MAX_AGE", 300)
CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")
CORS_EXTRA_ORIGINS = os.getenv("CORS_EXTRA_ORIGINS", [])
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", [])
CORS_EXPOSE_HEADERS = os.getenv("CORS_EXPOSE_HEADERS", [])
DDB_TABLE_NAME = os.getenv("TABLE_NAME", "cloud_pass")
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
cp_ddb = DDB(DDB_TABLE_NAME)


# Lambda Routes
@app.exception_handler(ValidationError)
def incorrect_input_dataype(exc: ValidationError):
    """Handle invalid request parameters"""
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
    """Lambda function route to handle unknown routes"""
    logger.info(f"Route: {app.current_event.path} Not found")
    return Response(
        status_code=HTTPStatus.NOT_FOUND.value,
        content_type=content_types.TEXT_PLAIN,
        body=HTTPStatus.NOT_FOUND.phrase,
    )


@app.get("/")
def health_check():
    """Lambda function route to handle health checks"""
    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=HTTPStatus.OK.phrase,
    )


@app.put("/rules/regex")
@tracer.capture_method
def put_regex_rules():
    """Lambda function route to store regex rules into DDB table"""
    event_body = (
        app.current_event._data.body  # pylint: disable=W0212
        if app.current_event._data.body  # pylint: disable=W0212
        else {}
    )

    regex_rules = event_body.get("regex_rules", [])
    if regex_rules:
        regex_rules: RegexRulesModel = parse(
            model=RegexRulesModel, event=event_body
        ).regex_rules
        processed_regex_rules = []
        for i, rule in enumerate(regex_rules):
            regex_rules = {}
            regex_rules["pk"] = "RGX_RULES"  # DDB Hash Key
            regex_rules["sk"] = f"RGX_{str(ulid.new())}"  # DDB Secondary Key
            regex_rules["priority"] = i
            regex_rules["regex"] = rule
            regex_rules = recursive_process_dict(regex_rules)
            processed_regex_rules.append(regex_rules)
        cp_ddb.batch_put_items(processed_regex_rules)
        return Response(
            status_code=HTTPStatus.OK.value,
            content_type=content_types.APPLICATION_JSON,
            body=HTTPStatus.OK.phrase,
        )
    return Response(
        status_code=HTTPStatus.NO_CONTENT.value,
        content_type=content_types.APPLICATION_JSON,
        body=HTTPStatus.NO_CONTENT.phrase,
    )


@app.get("/rules/regex")
@tracer.capture_method
def get_regex_rules():
    """Lambda function route to query regex rules stored in DDB table.
    The regex rules are queried from DDB, then each item's attribute
    datatypes are altered to an acceptal JSONifyable datatype.

    Returns
    -------

        - processed_regex_rules: list[dict]
            list of objects representing queried DynamoDB items
    """
    hash_key_name = "RGX_RULES"
    range_key_prefix = "RGX_"
    projection_expression = "priority,regex"
    queried_regex_rules = cp_ddb.batch_query_items(
        hash_key_name, range_key_prefix, projection_expression
    )
    processed_regex_rules = [recursive_process_dict(x) for x in queried_regex_rules]
    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=processed_regex_rules,
    )


# Lambda handler
@tracer.capture_lambda_handler
@event_source(data_class=APIGatewayProxyEvent)  # pylint: disable=E1120
@logger.inject_lambda_context(
    log_event=False,
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    """Function to create or retrieve regex rules for SSO permission
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
