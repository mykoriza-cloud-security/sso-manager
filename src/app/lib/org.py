"""
Module to interact with the AWS Organizations service
"""
import boto3

class ORG:
    def __init__(self) -> None:
        self._org_client = boto3.client("organizations")
    
    def list_aws_accounts(self, max_results: int = 50):
        """
        Method to list AWS accounts
        """
        active_aws_accounts = []
        pagination_token = None

        # Paginate (if any) and retrieve all SSO groups
        while True:
            list_accounts_params = {
                "MaxResults": max_results,
                "IdentityStoreId": self._identity_store_id,
            }

            if pagination_token:
                list_accounts_params["NextToken"] = pagination_token

            response = self._org_client.list_accounts(**list_accounts_params)
            aws_accounts = response.get("Accounts", [])
            active_accounts = [x for x in aws_accounts if x["Status"] == "ACTIVE"]
            pagination_token = response.get("NextToken", None)
            active_aws_accounts.extend(active_accounts)

            if not pagination_token:
                break

        return active_aws_accounts
