import os
import json
import moto
import boto3
import pytest
from src.app.lib.utils import generate_lambda_context

################################################
#         Fixtures - AWS Env & Env Vars        #
################################################

@pytest.fixture(scope="session", autouse=True)
def set_aws_creds():
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "test")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    yield

@pytest.fixture(scope="session", autouse=True)
def setup_env_vars():
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("DDB_TABLE_NAME", "cloud_pass")
    monkeypatch.setenv("IDENTITY_STORE_ID", "d-1234567890")
    monkeypatch.setenv("IDENTITY_STORE_ARN", "arn:aws:sso:::instance/ssoins-instanceId")
    yield

@pytest.fixture(autouse=True)
def context():
    return generate_lambda_context()


################################################
#         Fixtures - AWS organizations         #
################################################


def create_aws_ous_accounts(
    organizations_client: boto3.client,
    aws_organization_definitions: list[dict],
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


@pytest.fixture(scope="session")
def load_organization_definition() -> dict:
    cwd = os.path.dirname(os.path.realpath(__file__))
    organizations_map_path = os.path.join(cwd, "./configs/aws_organizations_details.json")
    with open(organizations_map_path, "r") as fp:
        return json.load(fp)

@pytest.fixture(scope="session")
def organizations_client() -> boto3.client:
    """
    Fixture to mock AWS Organizations client
    """
    with moto.mock_organizations():
        yield boto3.client("organizations")

@pytest.fixture(scope="session")
def setup_aws_organization(load_organization_definition, organizations_client) -> dict:

    # Create AWS organization
    organizations_client.create_organization()
    root_ou_id = organizations_client.list_roots()["Roots"][0]["Id"]

    # Create AWS OUs & accounts
    aws_organization_definitions = load_organization_definition["organization_definition"]
    create_aws_ous_accounts(organizations_client, aws_organization_definitions, root_ou_id)
    
    # Return AWS organization details
    return {
        "root_ou_id": root_ou_id,
        "aws_organizations_client": organizations_client,
        "aws_organization_definitions": aws_organization_definitions
    }


################################################
#        Fixtures - AWS Identity Center        #
################################################


@pytest.fixture(scope="session")
def identity_store_client() -> boto3.client:
    """
    Fixture to mock AWS Organizations client
    """
    with moto.mock_identitystore():
        yield boto3.client("identitystore")

@pytest.fixture(scope="session")
def sso_admin_client() -> boto3.client:
    """
    Fixture to mock AWS Organizations client
    """
    with moto.mock_ssoadmin():
        yield boto3.client("sso-admin")

@pytest.fixture(scope="session")
def load_sso_groups_definitions() -> dict:
    cwd = os.path.dirname(os.path.realpath(__file__))
    load_sso_groups_definitions_path = os.path.join(cwd, "./configs/aws_sso_groups_details.json")
    with open(load_sso_groups_definitions_path, "r") as fp:
        return json.load(fp)

@pytest.fixture(scope="session")
def load_permission_sets_definitions() -> dict:
    cwd = os.path.dirname(os.path.realpath(__file__))
    load_permission_sets_definitions_path = os.path.join(cwd, "./configs/aws_permission_set_details.json")
    with open(load_permission_sets_definitions_path, "r") as fp:
        return json.load(fp)

@pytest.fixture(scope="session")
def setup_identity_store(
    identity_store_client: boto3.client,
    sso_admin_client: boto3.client,
    load_sso_groups_definitions: dict,
    load_permission_sets_definitions: dict,
):

    # Create SSO groups
    identity_store_id = os.getenv("IDENTITY_STORE_ID")
    for group in load_sso_groups_definitions["sso_groups_definitions"]:
        identity_store_client.create_group(
            IdentityStoreId=identity_store_id,
            DisplayName=group["name"],
            Description=group["description"]
        )

    # Create permission sets
    identity_store_arn = os.getenv("IDENTITY_STORE_ARN")
    for permission_set in load_permission_sets_definitions["permission_sets_definitions"]:
        sso_admin_client.create_permission_set(
            InstanceArn=identity_store_arn,
            Name=permission_set["name"],
            Description=permission_set["description"]
        )
    
    return {
        "identity_store_client": identity_store_client,
        "sso_admin_client": sso_admin_client,
        "sso_groups_definitions": load_sso_groups_definitions["sso_groups_definitions"],
        "permission_sets_definitions": load_permission_sets_definitions["permission_sets_definitions"]
    }

################################################
#              Fixtures - DynamoDB             #
################################################
