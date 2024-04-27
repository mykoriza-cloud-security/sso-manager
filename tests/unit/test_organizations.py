"""
Unit tests to test writing regex rules from DDB
"""
import os
import json
import itertools
import moto
import boto3
import pytest
from typing import Dict
from src.app.lib.aws_organizations import AwsOrganizations

################################################
#                   Fixtures                   #
################################################


@pytest.fixture(autouse=True)
def get_organization_map() -> Dict:
    cwd = os.path.dirname(os.path.realpath(__file__))
    organizations_map_path = os.path.join(cwd, "aws_organizations_details.json")
    with open(organizations_map_path, "r") as fp:
        return json.load(fp)


@pytest.fixture(autouse=True)
def organizations_client(set_aws_creds) -> boto3.client:
    """
    Fixture to mock AWS Organizations client
    """
    with moto.mock_organizations():
        yield boto3.client("organizations")


@pytest.fixture(autouse=True)
def create_aws_organization(get_organization_map: dict, organizations_client: boto3.client) -> str:
    organizations_client.create_organization()
    root_ou_id = organizations_client.list_roots()["Roots"][0]["Id"]
    aws_organization_definitions = get_organization_map["organization_definition"]
    create_aws_ous_accounts(organizations_client, aws_organization_definitions, root_ou_id)
    return root_ou_id


################################################
#                    Helpers                   #
################################################


def create_aws_ous_accounts(
    organizations_client: boto3.client,
    aws_organization_definitions: list,
    root_ou_id: str,
    parent_ou_id: str = ""
) -> None:
    """
    Fixture to setup AWS mock organizations by creating:
        1. Creating an AWS organization
        2. Creating AWS organizations units (OUs)
        3. Creating AWS accounts
        4. Moving those AWS accounts under their designated OU
    """
    for organization_resource in aws_organization_definitions:

        if organization_resource["type"] == "ORGANIZATIONAL_UNIT":
            # Create OU
            nested_ou_id = organizations_client.create_organizational_unit(
                ParentId=parent_ou_id if parent_ou_id else root_ou_id,
                Name=organization_resource["name"],
            )["OrganizationalUnit"]["Id"]

            # Recursively setup OU
            if organization_resource["children"]:
                create_aws_ous_accounts(
                    organizations_client, organization_resource["children"], root_ou_id, nested_ou_id
                )

        elif organization_resource["type"] == "ACCOUNT":
            # Create account
            account_id = organizations_client.create_account(
                Email=f"{organization_resource['name']}@testing.com",
                AccountName=organization_resource["name"],
            )["CreateAccountStatus"]["AccountId"]

            # Move account to OU
            organizations_client.move_account(
                AccountId=account_id,
                SourceParentId=root_ou_id,
                DestinationParentId=parent_ou_id,
            )


################################################
#                     Tests                    #
################################################


def test_list_active_aws_accounts_include_all_organiational_units(create_aws_organization: str) -> None:
    # Arrange
    root_ou_id = create_aws_organization
    py_aws_organizations = AwsOrganizations(root_ou_id)

    # Act
    aws_organizations_map = py_aws_organizations.describe_aws_organizational_unit()
    active_aws_accounts_via_class = list(itertools.chain(*aws_organizations_map.values()))
    active_aws_accounts_via_boto3 = boto3.client("organizations").list_accounts()["Accounts"]

    # Assert
    assert len(active_aws_accounts_via_class) == len(active_aws_accounts_via_boto3)    


def test_list_active_aws_accounts_include_specific_organiational_unit(
    organizations_client: boto3.client, 
    create_aws_organization: str,
    get_organization_map: dict
) -> None:
    # Arrange
    include_ou_name = "prod"
    root_ou_id = create_aws_organization
    py_aws_organizations = AwsOrganizations(root_ou_id)

    # Act
    root_ou_id = organizations_client.list_roots()["Roots"][0]["Id"]
    organizational_units_via_boto3 = boto3.client("organizations").list_organizational_units_for_parent(ParentId=root_ou_id)["OrganizationalUnits"]
    target_child_ou_id = next((obj["Id"] for obj in organizational_units_via_boto3 if obj["Name"] == include_ou_name))
    aws_organizations_map = py_aws_organizations.describe_aws_organizational_unit(parent_ou_id=target_child_ou_id)

    active_aws_accounts_via_class = list(itertools.chain(*aws_organizations_map.values()))
    expected_aws_accounts_via_local_org_map = list(next((obj["children"] for obj in get_organization_map["organization_definition"] if obj["name"] == include_ou_name)))

    # Assert
    assert len(active_aws_accounts_via_class) == len(expected_aws_accounts_via_local_org_map)


def test_list_active_aws_accounts_exclude_suspended_organizational_unit(
    organizations_client: boto3.client,
    create_aws_organization: str,
    get_organization_map: dict
) -> None:
    # Arrange
    ignore_ou_name = "suspended"
    root_ou_id = create_aws_organization
    py_aws_organizations = AwsOrganizations(root_ou_id)

    # Act
    root_ou_id = organizations_client.list_roots()["Roots"][0]["Id"]
    organizational_units_via_boto3 = organizations_client.list_organizational_units_for_parent(ParentId=root_ou_id)["OrganizationalUnits"]
    
    suspended_ou_id = next((obj["Id"] for obj in organizational_units_via_boto3 if obj["Name"] == ignore_ou_name))
    suspended_ou_accounts = list(next((obj["children"] for obj in get_organization_map["organization_definition"] if obj["name"] == ignore_ou_name), []))
    aws_organizations_map = py_aws_organizations.describe_aws_organizational_unit(ou_ignore_list=[suspended_ou_id])

    active_aws_accounts_via_class = list(itertools.chain(*aws_organizations_map.values()))
    active_aws_accounts_via_boto3 = boto3.client("organizations").list_accounts()["Accounts"]

    # Assert
    assert len(active_aws_accounts_via_class) == len(active_aws_accounts_via_boto3) - len(suspended_ou_accounts)