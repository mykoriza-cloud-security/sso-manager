"""
Module to interact with the AWS Organizations service
"""
import boto3


class AwsOrganizations:
    def __init__(self) -> None:
        self._organizations_client = boto3.client("organizations")

    def list_aws_accounts(self, max_results: int = 50):
        """
        Method to list AWS accounts
        """
        active_aws_accounts = []
        pagination_token = None
        boto3_list_accounts_params = {"MaxResults": max_results}

        # Paginate (if any) and retrieve all SSO groups
        while True:

            if pagination_token:
                boto3_list_accounts_params["NextToken"] = pagination_token

            response = self._organizations_client.list_accounts(**boto3_list_accounts_params)
            aws_accounts = response.get("Accounts", [])
            active_accounts = [x for x in aws_accounts if x["Status"] == "ACTIVE"]
            pagination_token = response.get("NextToken", None)
            active_aws_accounts.extend(active_accounts)

            if not pagination_token:
                break

        return active_aws_accounts
