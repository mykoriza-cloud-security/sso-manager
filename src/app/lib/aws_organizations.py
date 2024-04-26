"""
Module to interact with the AWS Organizations service
"""
import boto3


class AwsOrganizations:
    def __init__(self) -> None:
        self._organizations_client = boto3.client("organizations")
        self._root_ou_id = self._organizations_client.list_roots()["Roots"][0]["Id"]


    def describe_aws_organizational_unit(self, parent_ou_id: str = "", ou_ignore_list: list = []):

        # Get List of all OUs
        ou_list = []
        parent_id = parent_ou_id if parent_ou_id else self._root_ou_id
        boto3_ou_paginator = self._organizations_client.get_paginator("list_children")
        boto3_ou_iterator  = boto3_ou_paginator.paginate(ParentId = parent_id, ChildType = "ORGANIZATIONAL_UNIT")
        for page in boto3_ou_iterator:
            for ou in page["Children"]:
                if ou["Id"] not in ou_ignore_list:
                    ou_list.append(ou["Id"])
                    ou_list.extend(self.describe_aws_organizational_unit(ou["Id"]))
        ou_list.append(parent_id)
        
        # Create map of AWS accounts to OUs
        ou_accounts_map = {}
        boto3_accounts_paginator = self._organizations_client.get_paginator("list_accounts_for_parent")
        for ou_id in ou_list:
            ou_accounts_map[ou_id] = []
            boto3_accounts_iterator = boto3_accounts_paginator.paginate(ParentId = ou_id)
            for page in boto3_accounts_iterator:
                for account in page["Accounts"]:
                    if account["Status"] == "ACTIVE":
                        account_information = {"Id": account["Id"], "Name": account["Name"]}
                        ou_accounts_map[ou_id].append(account_information)

        return ou_accounts_map
