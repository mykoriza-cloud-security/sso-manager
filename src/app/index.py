"""
Regex based rules engine for processing regex input for the
purpose of assiging permission sets.
"""
import os
from http import HTTPStatus

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source

# Local package & layer imports
from .lib.aws_dynamodb import DDB
from .lib.aws_organizations import AwsOrganizations
from .lib.aws_identitycenter import AwsIdentityCenter

# Env vars
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DDB_TABLE_NAME = os.getenv("TABLE_NAME", "cloud_pass")
TRACER_SERVICE_NAME = os.getenv("TRACER_SERVICE_NAME", "regex_rules_microservice")
IMPLICIT_RULES_PK = os.getenv("IMPLICIT_RULES_PK", "IMPLICIT")
IMPLICIT_RULES_SK_PREFIX = os.getenv("IMPLICIT_RULES_PK", "IMP_")

# AWS Lambda powertool objects & class instances
TRACER = Tracer(service=TRACER_SERVICE_NAME)
LOGGER = Logger(service=TRACER_SERVICE_NAME, level=LOG_LEVEL)

py_org = AwsOrganizations()
py_sso = AwsIdentityCenter()
py_ddb = DDB(DDB_TABLE_NAME)


# Lambda Routes
@TRACER.capture_method
def put_rbac_sso_assignments():
    """
    Lambda function route to create RBAC permission set
    Assignments.
    """

    sso_groups = py_sso.get_sso_groups()
    # permission_sets = py_sso.get_permission_sets()
    # active_aws_accounts = py_org.list_aws_accounts()
    # assignment_rules = py_ddb.batch_query_items(
    #     IMPLICIT_RULES_PK, IMPLICIT_RULES_SK_PREFIX, projection_expression="rule,type"
    # )

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=sso_groups,
    )


# Lambda handler
@TRACER.capture_lambda_handler
@event_source(data_class=EventBridgeEvent)  # pylint: disable=E1120
@LOGGER.inject_lambda_context(
    log_event=True,
    correlation_id_path=correlation_paths.EVENT_BRIDGE,
)
def lambda_handler(event: EventBridgeEvent, context: LambdaContext):
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
    # return put_rbac_sso_assignments(event, context)
    return True
