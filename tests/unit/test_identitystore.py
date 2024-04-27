"""
Unit tests to test writing regex rules from DDB
"""
import os
import json
import moto
import boto3
import pytest
from typing import NoReturn
from src.app.lib.aws_identitystore import AwsIdentityStore


################################################
#                   Fixtures                   #
################################################


@pytest.fixture(autouse=True)
def sso_admin_client(set_aws_creds) -> boto3.client:
    """
    Fixture to mock AWS Organizations client
    """
    with moto.mock_ssoadmin():
        yield boto3.client("sso-admin")


@pytest.fixture(autouse=True)
def identity_store_client(set_aws_creds) -> boto3.client:
    """
    Fixture to mock AWS Organizations client
    """
    with moto.mock_identitystore():
        yield boto3.client("identitystore")


################################################
#                    Helpers                   #
################################################


@pytest.fixture(autouse=True)
def sso_groups_definitions() -> dict:
    cwd = os.path.dirname(os.path.realpath(__file__))
    sso_groups_definitions_path = os.path.join(cwd, "aws_sso_groups_details.json")
    with open(sso_groups_definitions_path, "r") as fp:
        return json.load(fp)


@pytest.fixture(autouse=True)
def permission_set_definitions() -> dict:
    cwd = os.path.dirname(os.path.realpath(__file__))
    permission_set_definitions_path = os.path.join(cwd, "aws_permission_set_details.json")
    with open(permission_set_definitions_path, "r") as fp:
        return json.load(fp)


@pytest.fixture(autouse=True)
def create_sso_groups(sso_groups_definitions: dict, identity_store_client: boto3.client) -> None:
    """
    Fixture to create SSO groups
    """
    identity_store_id = os.getenv("IDENTITY_STORE_ID")
    for group in sso_groups_definitions["group_definitions"]:
        identity_store_client.create_group(
            IdentityStoreId=identity_store_id,
            DisplayName=group["name"],
            Description=group["description"]
        )


@pytest.fixture(autouse=True)
def create_permission_sets(permission_set_definitions: dict, sso_admin_client: boto3.client) -> None:
    identity_store_arn = os.getenv("IDENTITY_STORE_ARN")
    for permission_set in permission_set_definitions["permission_set_definitions"]:
        sso_admin_client.create_permission_set(
            InstanceArn=identity_store_arn,
            Name=permission_set["name"],
            Description=permission_set["description"]
        )


################################################
#                     Tests                    #
################################################


def test_missing_constructor_identity_store_id_parameter() -> None:
    # Arrange
    identity_store_arn = os.getenv("IDENTITY_STORE_ARN")

    # Assert
    with pytest.raises(TypeError):
        AwsIdentityStore(identity_store_arn=identity_store_arn)


def test_missing_constructor_identity_store_arn_parameter() -> None:
    # Arrange
    identity_store_id = os.getenv("IDENTITY_STORE_ID")

    # Assert
    with pytest.raises(TypeError):
        AwsIdentityStore(identity_store_id=identity_store_id)


def test_missing_constructor_parameters() -> None:
    # Assert
    with pytest.raises(TypeError):
        AwsIdentityStore()


def test_list_sso_groups(sso_groups_definitions: dict, create_sso_groups: NoReturn) -> None:
    """
    Test list SSO groups
    """
    # Arrange
    identity_store_id = os.getenv("IDENTITY_STORE_ID")
    identity_store_arn = os.getenv("IDENTITY_STORE_ARN")
    py_aws_organizations = AwsIdentityStore(identity_store_id, identity_store_arn)

    # Act
    sso_groups = py_aws_organizations.list_sso_groups()
    
    # Assert
    assert len(sso_groups) == len(sso_groups_definitions["group_definitions"])


def test_list_permission_sets(permission_set_definitions: dict, create_sso_groups: NoReturn) -> None:
    """
    Test list SSO groups
    """
    # Arrange
    identity_store_id = os.getenv("IDENTITY_STORE_ID")
    identity_store_arn = os.getenv("IDENTITY_STORE_ARN")
    py_aws_organizations = AwsIdentityStore(identity_store_id, identity_store_arn)

    # Act
    permission_sets = py_aws_organizations.list_permission_sets()
    
    # Assert
    assert len(permission_sets) == len(permission_set_definitions["permission_set_definitions"])
