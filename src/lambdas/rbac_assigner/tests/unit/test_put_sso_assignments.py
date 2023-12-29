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
import boto3
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

# Local package imports
from cloud_pass.ddb import DDB
from cloud_pass.sso import SSO
from cloud_pass.utils import generate_lambda_context, create_table, delete_table

# Globals
IDENTITY_STORE_ID = "d-1234567890"
IDENTITY_STORE_ARN = "arn:aws:sso:::instance/ssoins-instanceId"

DDB_TABLE_NAME = "cloud_pass"
IDEMPOTENCY_DDB_TABLE_NAME = "cloud_pass_idempotency_store"

CURRENT_DIR = pathlib.Path(__file__).parent.resolve()

@moto.mock_dynamodb
@moto.mock_ssoadmin
@moto.mock_identitystore
@moto.mock_organizations
class TestPutSsoAssignments(unittest.TestCase):
    """
    Class to test writing regex rules to DDB
    """

    def setUp(self) -> None:
        """
        Creates DDB table, writes sample data to DDB table, and
        lambda context prior to test case execution
        """

        # Boto3 clients
        self._sso_admin_client = boto3.client("sso-admin")
        self._identity_store_client = boto3.client("identitystore")
        self._organizations_client = boto3.client("organizations")

        # Object instances
        self._py_ddb = DDB(DDB_TABLE_NAME)
        self._py_ids = SSO(IDENTITY_STORE_ID)
        self._lambda_context = generate_lambda_context()

        # Util method executions
        self._create_sso_groups()
        self._create_permission_sets()
        self._create_aws_root_organization()
        self._create_aws_accounts()
        create_table(table_name=IDEMPOTENCY_DDB_TABLE_NAME, primary_key="id")
        create_table(table_name=DDB_TABLE_NAME, primary_key="pk", secondary_key="sk")

    def tearDown(self) -> None:
        """
        Delete DDB table after test case execution
        """
        delete_table(DDB_TABLE_NAME)
        delete_table(IDEMPOTENCY_DDB_TABLE_NAME)

    def _create_sso_groups(self) -> list:
        """
        Create SSO groups from list of names provided in JSON docs.
        """
        sso_group_names = ["AWS_DIGITAL_FORENSICS-SECURITY-AUDIT-Admins", "AWS_INCIDENT_RESPONSE-SECURITY-AUDIT-Admins", "AWS_SECURITY_ANALYTICS-SECURITY-LOGGING-ReadOnly", "AWS_THREAT_INTELLIGENCE-SECURITY-LOGGING-ReadOnly"]
        for name in sso_group_names:
            self._identity_store_client.create_group(
                DisplayName=name,
                IdentityStoreId=IDENTITY_STORE_ID
            )

    def _create_permission_sets(self) -> None:
        permission_set_names = ["Admins", "PowerUser", "Security", "ReadOnly"]
        for name in permission_set_names:
            self._sso_admin_client.create_permission_set(
                Name=name,
                InstanceArn=IDENTITY_STORE_ARN)

    def _create_aws_root_organization(self) -> None:
        self._organizations_client.create_organization()

    def _create_aws_organizational_units(self) -> None:
        ou_names = []
        for name in ou_names:
            self._organizations_client.create_organizational_unit(
                Name=name,
                ParentId=
            )

    def _create_aws_accounts(self) -> None:
        aws_account_names = ["AUDIT", "LOGGING"]
        for name in aws_account_names:
            self._organizations_client.create_account(
                AccountName=name,
                Email=f"testing+{name}@testing.com"
            )

    def test(self) -> None:
        pass