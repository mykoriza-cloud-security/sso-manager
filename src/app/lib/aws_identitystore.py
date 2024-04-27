"""
Module to interact with the AWS IAM Identity Store service
"""
import itertools
import boto3


class AwsIdentityStore:
    def __init__(self, identity_store_id: str, identity_store_arn: str) -> None:
        """
        Default constructor method to initialize
        identity store variable and boto3 client.
        """
        self._identity_store_id = identity_store_id
        self._identity_store_arn = identity_store_arn

        self._identity_store_client = boto3.client("identitystore")
        self._sso_groups_pagniator = self._identity_store_client.get_paginator(
            "list_groups"
        )

        self._sso_admin_client = boto3.client("sso-admin")
        self._permission_sets_pagniator = self._sso_admin_client.get_paginator(
            "list_permission_sets"
        )

    def list_sso_groups(self):
        aws_identitystore_groups_iterator = self._sso_groups_pagniator.paginate(
            IdentityStoreId=self._identity_store_id
        )
        return list(
            itertools.chain.from_iterable(
                (page["Groups"] for page in aws_identitystore_groups_iterator)
            )
        )

    def list_permission_sets(self):
        """
        Method to list permission sets and remove sensitive information.
        """
        aws_permission_sets_iterator = self._permission_sets_pagniator.paginate(
            InstanceArn=self._identity_store_arn
        )
        return list(
            itertools.chain.from_iterable(
                (page["PermissionSets"] for page in aws_permission_sets_iterator)
            )
        )
