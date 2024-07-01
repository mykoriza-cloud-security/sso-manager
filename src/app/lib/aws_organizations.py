"""
Module to interact with the AWS Organizations service
"""
import itertools
import boto3


class AwsOrganizations:
    def __init__(self, root_ou_id: str, ou_id_ignore_list: list = []) -> None:

        # Set instance vars
        self.ou_account_map = {}
        self._root_ou_id = root_ou_id
        self._ou_id_ignore_list = ou_id_ignore_list

        # Set boto3 clients
        self._organizations_client = boto3.client("organizations")

        # Set paginators
        self._account_paginator = self._organizations_client.get_paginator("list_accounts_for_parent")
        self._ou_paginator = self._organizations_client.get_paginator("list_organizational_units_for_parent")

        # Create Account & OU itenerary
        self._describe_aws_organizational_unit(self._root_ou_id)

    def _describe_aws_organizational_unit(self, parent_ou_id: str = "") -> None:
        parent_ou_id = parent_ou_id if parent_ou_id else self._root_ou_id
        self.ou_account_map.setdefault(parent_ou_id, [])
        
        # Populate active accounts under parent ou ID
        accounts_iterator = self._account_paginator.paginate(ParentId=parent_ou_id)
        aws_accounts_flattened_list = list(itertools.chain.from_iterable((page["Accounts"] for page in accounts_iterator)))
        for account in aws_accounts_flattened_list:
            if account["Status"] == "ACTIVE":
                account_information = {"Id": account["Id"], "Name": account["Name"]}
                self.ou_account_map[parent_ou_id].append(account_information)
        
        # Recursively get list of nested OUs
        aws_ou_iterator = self._ou_paginator.paginate(ParentId=parent_ou_id)
        aws_ous_flattened_list = list(itertools.chain.from_iterable((page["OrganizationalUnits"] for page in aws_ou_iterator)))
        for ou in aws_ous_flattened_list:
            if ou["Id"] not in self._ou_id_ignore_list:
                self._describe_aws_organizational_unit(ou["Id"])
