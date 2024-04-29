"""
Unit tests to test writing regex rules from DDB
"""
import os
import pytest
from src.app.lib.aws_identitystore import AwsIdentityStore


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


def test_list_sso_groups(setup_identity_store: pytest.fixture) -> None:
    """
    Test list SSO groups
    """
    # Arrange
    identity_store_id = os.getenv("IDENTITY_STORE_ID")
    identity_store_arn = os.getenv("IDENTITY_STORE_ARN")
    sso_groups_definitions = setup_identity_store["sso_groups_definitions"]
    py_aws_sso = AwsIdentityStore(identity_store_id, identity_store_arn)

    # Act
    sso_groups = py_aws_sso.list_sso_groups()
    
    # Assert
    assert len(sso_groups) == len(sso_groups_definitions)


# def test_list_permission_sets(permission_set_definitions: dict, create_sso_groups: NoReturn) -> None:
#     """
#     Test list SSO groups
#     """
#     # Arrange
#     identity_store_id = os.getenv("IDENTITY_STORE_ID")
#     identity_store_arn = os.getenv("IDENTITY_STORE_ARN")
#     py_aws_organizations = AwsIdentityStore(identity_store_id, identity_store_arn)

#     # Act
#     permission_sets = py_aws_organizations.list_permission_sets()
    
#     # Assert
#     assert len(permission_sets) == len(permission_set_definitions["permission_set_definitions"])
