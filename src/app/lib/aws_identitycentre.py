"""
Module to interact with the AWS IAM Identity Store service
"""
import itertools
import boto3


class AwsIdentityCentre:
    def __init__(self, identity_store_id: str, identity_store_arn: str) -> None:
        """
        Default constructor method to initialize
        identity store variable and boto3 client.
        """

        # Set class instance vars
        self._identity_store_id = identity_store_id
        self._identity_store_arn = identity_store_arn

        # Set boto3 clients
        self._sso_admin_client = boto3.client("sso-admin")
        self._identity_store_client = boto3.client("identitystore")

        # Set paginators
        self._sso_users_paginator = self._identity_store_client.get_paginator("list_users")
        self._sso_groups_paginator = self._identity_store_client.get_paginator("list_groups")
        self._permission_sets_paginator = self._sso_admin_client.get_paginator("list_permission_sets")

        # Get Identity center entities
        self.sso_users = self._list_sso_users()
        self.sso_groups = self._list_sso_groups()
        self.permission_sets = self._list_permission_sets()

    def _list_sso_groups(self):
        aws_identitystore_groups_iterator = self._sso_groups_paginator.paginate(
            IdentityStoreId=self._identity_store_id
        )
        return list(
            itertools.chain.from_iterable(
                (page["Groups"] for page in aws_identitystore_groups_iterator)
            )
        )

    def _list_sso_users(self):
        """
        Method to list all the users in the identity store.
        """
        aws_identitystore_users_iterator = self._sso_users_paginator.paginate(
            IdentityStoreId=self._identity_store_id
        )
        return list(
            itertools.chain.from_iterable(
                (page["Users"] for page in aws_identitystore_users_iterator)
            )
        )

    def _list_permission_sets(self):
        """
        Method to list permission sets and remove sensitive information.
        """
        aws_permission_sets_iterator = self._permission_sets_paginator.paginate(
            InstanceArn=self._identity_store_arn
        )
        return list(
            itertools.chain.from_iterable(
                (page["PermissionSets"] for page in aws_permission_sets_iterator)
            )
        )
