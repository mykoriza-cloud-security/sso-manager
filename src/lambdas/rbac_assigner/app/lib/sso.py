"""
Module to interact with the AWS IAM Identity Store service
"""
import boto3

class SSO:

    def __init__(self, identity_store_id: str) -> None:
        """
        Default constructor method to initialize
        identity store variable and boto3 client.
        """
        self._identity_store_id = identity_store_id
        self._identity_store_client = boto3.client("identitystore")

    def get_sso_groups(self, max_results=50):
        """
        Method to list SSO groups.
        """
        sso_groups = []
        next_token = None
        while True:
            response = self._identity_store_client.list_groups(
                IdentityStoreId=self._identity_store_id,
                MaxResults=max_results,
                NextToken=next_token
            )

            groups = response.get("Groups", [])
            next_token = response.get("NextToken", "")
            sso_groups.extend(groups)

            if not next_token:
                return sso_groups
