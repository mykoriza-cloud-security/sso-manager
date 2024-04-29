"""
Unit tests to test writing regex rules from DDB
"""
import itertools
import pytest
from src.app.lib.aws_organizations import AwsOrganizations


def test_missing_constructor_parameter() -> None:
    # Arrange
    with pytest.raises(TypeError):
        AwsOrganizations()


def test_list_active_aws_accounts_include_all_organiational_units(setup_aws_organization: pytest.fixture) -> None:
    # Arrange
    root_ou_id = setup_aws_organization["root_ou_id"]
    organizations_client = setup_aws_organization["aws_organizations_client"]
    py_aws_organizations = AwsOrganizations(root_ou_id)

    # Act
    aws_organizations_map = py_aws_organizations.describe_aws_organizational_unit()
    active_aws_accounts_via_class = list(itertools.chain(*aws_organizations_map.values()))
    active_aws_accounts_via_boto3 = organizations_client.list_accounts()["Accounts"]

    # Assert
    assert len(active_aws_accounts_via_class) == len(active_aws_accounts_via_boto3)    


def test_list_active_aws_accounts_include_specific_organiational_unit(setup_aws_organization: pytest.fixture) -> None:
    # Arrange
    include_ou_name = "prod"
    root_ou_id = setup_aws_organization["root_ou_id"]
    organization_map = setup_aws_organization["aws_organization_definitions"]
    organizations_client = setup_aws_organization["aws_organizations_client"]
    py_aws_organizations = AwsOrganizations(root_ou_id)

    # Act
    root_ou_id = organizations_client.list_roots()["Roots"][0]["Id"]
    organizational_units_via_boto3 = organizations_client.list_organizational_units_for_parent(ParentId=root_ou_id)["OrganizationalUnits"]
    target_child_ou_id = next((obj["Id"] for obj in organizational_units_via_boto3 if obj["Name"] == include_ou_name))
    aws_organizations_map = py_aws_organizations.describe_aws_organizational_unit(parent_ou_id=target_child_ou_id)

    active_aws_accounts_via_class = list(itertools.chain(*aws_organizations_map.values()))
    expected_aws_accounts_via_local_org_map = list(next((obj["children"] for obj in organization_map if obj["name"] == include_ou_name)))

    # Assert
    assert len(active_aws_accounts_via_class) == len(expected_aws_accounts_via_local_org_map)


def test_list_active_aws_accounts_exclude_suspended_organizational_unit(setup_aws_organization: pytest.fixture) -> None:
    # Arrange
    ignore_ou_name = "suspended"
    root_ou_id = setup_aws_organization["root_ou_id"]
    organization_map = setup_aws_organization["aws_organization_definitions"]
    organizations_client = setup_aws_organization["aws_organizations_client"]
    py_aws_organizations = AwsOrganizations(root_ou_id)

    # Act
    root_ou_id = organizations_client.list_roots()["Roots"][0]["Id"]
    organizational_units_via_boto3 = organizations_client.list_organizational_units_for_parent(ParentId=root_ou_id)["OrganizationalUnits"]
    
    suspended_ou_id = next((obj["Id"] for obj in organizational_units_via_boto3 if obj["Name"] == ignore_ou_name))
    suspended_ou_accounts = list(next((obj["children"] for obj in organization_map if obj["name"] == ignore_ou_name), []))
    aws_organizations_map = py_aws_organizations.describe_aws_organizational_unit(ou_ignore_list=[suspended_ou_id])

    active_aws_accounts_via_class = list(itertools.chain(*aws_organizations_map.values()))
    active_aws_accounts_via_boto3 = organizations_client.list_accounts()["Accounts"]

    # Assert
    assert len(active_aws_accounts_via_class) == len(active_aws_accounts_via_boto3) - len(suspended_ou_accounts)
