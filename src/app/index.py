"""
Regex based rules engine for processing regex input for the
purpose of assiging permission sets.
"""
import os
import itertools
from http import HTTPStatus

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source

# Local package & layer imports
from .lib.aws_dynamodb import DDB
from .lib.aws_organizations import AwsOrganizations
from .lib.aws_identitystore import AwsIdentityStore

# Env vars
LOG_LEVEL = os.getenv("LOG_LEVEL")
DDB_TABLE_NAME = os.getenv("TABLE_NAME")
TRACER_SERVICE_NAME = os.getenv("TRACER_SERVICE_NAME")

ROOT_OU_ID = os.getenv("ROOT_OU_ID")
IDENTITY_STORE_ID = os.getenv("IDENTITY_STORE_ID")
IDENTITY_STORE_ARN = os.getenv("IDENTITY_STORE_ARN")

# AWS Lambda powertool objects & class instances
TRACER = Tracer(service=TRACER_SERVICE_NAME)
LOGGER = Logger(service=TRACER_SERVICE_NAME, level=LOG_LEVEL)

py_ddb = DDB(DDB_TABLE_NAME)
py_aws_organizations = AwsOrganizations(ROOT_OU_ID)
py_aws_identitycenter = AwsIdentityStore(IDENTITY_STORE_ID, IDENTITY_STORE_ARN)


# Lambda Routes
def put_rbac_sso_assignments():
    """
    Lambda function route to create RBAC permission set
    Assignments.
    """

    # Get active AWS accounts
    aws_organizational_map = py_aws_organizations.describe_aws_organizational_unit()
    active_aws_accounts = list(itertools.chain(*aws_organizational_map.values()))

    # Get SSO groups & permission sets
    sso_groups = py_aws_identitycenter.list_sso_groups()
    permission_sets = py_aws_identitycenter.list_permission_sets()
    # assignment_rules = py_ddb.batch_query_items(
    #     IMPLICIT_RULES_PK, IMPLICIT_RULES_SK_PREFIX, projection_expression="rule,type"
    # )


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
    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        # body=sso_groups,
    )
