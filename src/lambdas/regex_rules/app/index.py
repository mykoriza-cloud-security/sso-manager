"""Regex based rules engine for processing regex input for the
purpose of assiging permission sets.
"""
import os
import ulid  # pylint: disable=E0401
from aws_lambda_powertools import Logger, Tracer  # pylint: disable=E0401
from aws_lambda_powertools.logging import correlation_paths  # pylint: disable=E0401
from aws_lambda_powertools.utilities.typing import (
    LambdaContext,
)  # pylint: disable=E0401

# from aws_lambda_powertools.utilities.parser import parse, validator                        # pylint: disable=E0401
from aws_lambda_powertools.utilities.validation import (
    SchemaValidationError,
)  # pylint: disable=E0401
from aws_lambda_powertools.utilities.data_classes import (
    event_source,
    APIGatewayProxyEvent,
)  # pylint: disable=E0401
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.event_handler import (
    Response,
    content_types,
    APIGatewayRestResolver,
)

# Local package & layer imports
from cloud_pass.ddb import DDB
from cloud_pass.utils import recursive_process_dict

# from .schemas import RegexRulesModel

# Env vars
DDB_TABLE_NAME = os.getenv("TABLE_NAME", "cloud_pass")
POWERTOOLS_LOGGER_LOG_EVENT = os.getenv(  # pylint: disable=W1508
    "POWERTOOLS_LOGGER_LOG_EVENT", True
)
TRACER_SERVICE_NAME = os.getenv("TRACER_SERVICE_NAME", "regex_rules_microservice")

# AWS Lambda powertool objects & class instances
logger = Logger()
app = APIGatewayRestResolver()
tracer = Tracer(service=TRACER_SERVICE_NAME)
cp_ddb = DDB(DDB_TABLE_NAME)


# Lambda Routes
@app.exception_handler(SchemaValidationError)
def incorrect_input_dataype(ex: SchemaValidationError):
    """Handle invalid request parameters"""
    metadata = {
        "path": app.current_event.path,
        "query_strings": app.current_event.query_string_parameters,
        "body": app.current_event.body,
    }
    logger.error(f"Malformed request: {ex}", extra=metadata)
    return Response(
        status_code=400,
        content_type=content_types.TEXT_PLAIN,
        body="Invalid request parameters",
    )


@app.not_found
@tracer.capture_method
def handle_not_found_errors(exc: NotFoundError) -> Response:  # pylint: disable=W0613
    """Lambda function route to handle unknown routes"""
    logger.info(f"Route: {app.current_event.path} Not found")
    return Response(
        status_code=404, content_type=content_types.TEXT_PLAIN, body="Route not found!"
    )


@app.get("/")
def health_check():
    """Lambda function route to handle healthchecks"""
    return "Health check!"


@app.put("/rules/regex")
# @validator("regex_rules")
@tracer.capture_method
def put_regex_rules():
    """Lambda function route to store regex rules into DDB table"""
    event_body = (
        app.current_event._data.body  # pylint: disable=W0212
        if app.current_event._data.body  # pylint: disable=W0212
        else {}
    )
    regex_rules = event_body.get("regex_rules", [])
    # parse(model=RegexRulesModel, event=regex_rules)
    if regex_rules:
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
        return "Batch write successul"
    return "No input provided"


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
    return processed_regex_rules


# Lambda handler
@tracer.capture_lambda_handler
@event_source(data_class=APIGatewayProxyEvent)  # pylint: disable=E1120
@logger.inject_lambda_context(
    log_event=POWERTOOLS_LOGGER_LOG_EVENT,
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
    logger.info(f"event: {event}")
    return app.resolve(event, context
