"""
Module to interact with the AWS IAM Identity Store service
"""
import os
import boto3


class AwsIdentityCenter:

    def __init__(self) -> None:
        """
        Default constructor method to initialize
        identity store variable and boto3 client.
        """
        self._sso_admin_client = boto3.client("sso-admin")
        self._identity_store_client = boto3.client("identitystore")
        self._identity_store_id = os.getenv("IDENTITY_STORE_ID", "d-1234567890")
        self._identity_store_arn = os.getenv("IDENTITY_STORE_ARN", "arn:aws:sso:::instance/ssoins-instanceId")

    def get_sso_groups(self, max_results: int = 50):
        """
        Method to list SSO groups and remove sensitive information.
        """
        sso_groups = []
        pagination_token = None
        boto3_list_groups_params = {"MaxResults": max_results, "IdentityStoreId": self._identity_store_id}

        # Paginate (if any) and retrieve all SSO groups
        while True:

            if pagination_token:
                boto3_list_groups_params["NextToken"] = pagination_token

            response = self._identity_store_client.list_groups(**boto3_list_groups_params)
            groups = response.get("Groups", [])
            pagination_token = response.get("NextToken", None)
            sso_groups.extend(groups)

            if not pagination_token:
                break

        return sso_groups

    def get_permission_sets(self, max_results: int = 50):
        """
        Method to list permission sets and remove sensitive information.
        """
        all_permission_sets = []
        permission_set_arns = []
        pagination_token = None
        boto3_list_permission_sets_params = {"MaxResults": max_results, "InstanceArn": self._identity_store_arn}

        # Paginate (if any) and retrieve all permission sets
        while True:

            if pagination_token:
                boto3_list_permission_sets_params["NextToken"] = pagination_token

            response = self._sso_admin_client.list_permission_sets(
                **boto3_list_permission_sets_params
            )
            permission_set_arns_chunk = response.get("PermissionSets", [])
            permission_set_arns.extend(permission_set_arns_chunk)

            if not pagination_token:
                break

        for arn in permission_set_arns:
            permission_set = self._sso_admin_client.describe_permission_set(
                PermissionSetArn=arn,
                InstanceArn=self._identity_store_arn,
            )["PermissionSet"]
            all_permission_sets.append(permission_set)

        return all_permission_sets

    def put_permission_set_assignments(self):
        pass
