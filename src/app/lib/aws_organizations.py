"""
Module to interact with the AWS Organizations service
"""
import itertools
import boto3


class AwsOrganizations:
    def __init__(self) -> None:
        self._organizations_client = boto3.client("organizations")
        self._root_ou_id = self._organizations_client.list_roots()["Roots"][0]["Id"]
        self._account_paginator = self._organizations_client.get_paginator("list_accounts_for_parent")
        self._ou_paginator = self._organizations_client.get_paginator("list_organizational_units_for_parent")


    def describe_aws_organizational_unit(self, parent_ou_id: str = "", ou_ignore_list: list = []):

        # Get List of all OUs
        ou_list = []
        parent_id = parent_ou_id if parent_ou_id else self._root_ou_id
        boto3_aws_ou_iterator = self._ou_paginator.paginate(ParentId = parent_id)
        boto3_aws_ous_flattened_list = list(itertools.chain.from_iterable((page["OrganizationalUnits"] for page in boto3_aws_ou_iterator)))
        for ou in boto3_aws_ous_flattened_list:
            if ou["Id"] not in ou_ignore_list:
                ou_list.append(ou["Id"])
                ou_list.extend(self.describe_aws_organizational_unit(ou["Id"], ou_ignore_list))
        ou_list.append(parent_id)
        
        # Create map of AWS accounts to OUs
        ou_accounts_map = {}
        for ou_id in ou_list:
            ou_accounts_map[ou_id] = []
            boto3_accounts_iterator = self._account_paginator.paginate(ParentId = ou_id)
            boto3_aws_accounts_flattened_list = list(itertools.chain.from_iterable((page["Accounts"] for page in boto3_accounts_iterator)))
            for account in boto3_aws_accounts_flattened_list:
                if account["Status"] == "ACTIVE":
                    account_information = {"Id": account["Id"], "Name": account["Name"]}
                    ou_accounts_map[ou_id].append(account_information)
        return ou_accounts_map
