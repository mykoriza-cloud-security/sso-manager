# """
# Unit tests to test writing regex rules from DDB
# """

# # Imports
# import moto
# import importlib # use importlib.reload(index)
# from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

# # Local package import
# from src.app.index import lambda_handler


# @moto.mock_ssoadmin
# @moto.mock_identitystore
# @moto.mock_organizations
# class TestPutSsoAssignments:

# #     """
# #     Class to test writing regex rules to DDB
# #     """

# #     def setUp(self) -> None:
# #         """
# #         Creates DDB table, writes sample data to DDB table, and
# #         lambda context prior to test case execution
# #         """

# #         # Boto3 clients
# #         self._sso_admin_client = boto3.client("sso-admin")
# #         self._identity_store_client = boto3.client("identitystore")

# #         # Get env vars
# #         self._identity_store_id = os.getenv("IDENTITY_STORE_ID")
# #         self._identity_store_arn = os.getenv("IDENTITY_STORE_ARN")

# #         # Object instances
# #         self._py_ids = SSO(self._identity_store_id, self._identity_store_arn)
# #         self._lambda_context = generate_lambda_context()

# #         # Class method executions
# #         self._create_aws_accounts()
# #         self._create_sso_groups()
# #         self._create_permission_sets()

# #         # Util method executions
# #         create_table(table_name=self._ddb_table_name, primary_key="pk", secondary_key="sk")

# #     def tearDown(self) -> None:
# #         """
# #         Delete DDB table after test case execution
# #         """
# #         delete_table(self._ddb_table_name)

# #     def _create_sso_groups(self) -> list:
# #         """
# #         Create SSO groups from list of names provided in JSON docs.
# #         """
# #         sso_group_names = [
# #             "AWS_DIGITAL_FORENSICS-SECURITY-AUDIT-Admins",
# #             "AWS_INCIDENT_RESPONSE-SECURITY-AUDIT-Admins",
# #             "AWS_SECURITY_ANALYTICS-SECURITY-LOGGING-ReadOnly",
# #             "AWS_THREAT_INTELLIGENCE-SECURITY-LOGGING-ReadOnly",
# #         ]
# #         for name in sso_group_names:
# #             self._identity_store_client.create_group(
# #                 DisplayName=name, IdentityStoreId=self._identity_store_id
# #             )

# #     def _create_permission_sets(self) -> None:
# #         permission_set_names = ["Admins", "PowerUser", "Security", "ReadOnly"]
# #         for name in permission_set_names:
# #             self._sso_admin_client.create_permission_set(
# #                 Name=name, InstanceArn=self._identity_store_id
# #             )



#     # def test(self, context) -> None:

#     #     # Act
#     #     event = EventBridgeEvent(data={})
#     #     response = lambda_handler(event, context)
#     #     assert response == True
