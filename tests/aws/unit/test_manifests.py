"""
Unit tests to test writing regex rules from DDB
"""
import os
import pytest
import jsonschema
from aws.app.lib.aws_sso_resolver import AwsResolver

# Globals vars
CWD = os.path.dirname(os.path.realpath(__file__))
MANIFEST_SCHEMA_DEFINITION_FILEPATH = os.path.join(
    CWD,
    "..",
    "..",
    "..",
    "src",
    "aws",
    "app",
    "schemas",
    "manifest_schema_definition.json",
)


# Test cases
def test_missing_rules() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD, "..", "configs", "manifests", "missing_rules.yaml"
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_single_rule_invalid_rules_target_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD, "..", "configs", "manifests", "single_rule_invalid_rules_target_type.yaml"
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_multiple_rules_invalid_rules_target_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD,
        "..",
        "configs",
        "manifests",
        "multiple_rules_invalid_rules_target_type.yaml",
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_single_rule_invalid_rules_access_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD, "..", "configs", "manifests", "single_rule_invalid_rules_access_type.yaml"
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_multiple_rules_invalid_rules_access_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD,
        "..",
        "configs",
        "manifests",
        "multiple_rules_invalid_rules_access_type.yaml",
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_single_rule_missing_permission_set_name() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD,
        "..",
        "configs",
        "manifests",
        "single_rule_missing_permission_set_name.yaml",
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_multiple_rules_missing_permission_set_name() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD,
        "..",
        "configs",
        "manifests",
        "multiple_rules_missing_permission_set_name.yaml",
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_single_rule_missing_principal_name() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD, "..", "configs", "manifests", "single_rule_missing_principal_name.yaml"
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_multiple_rules_missing_principal_name() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD, "..", "configs", "manifests", "multiple_rules_missing_principal_name.yaml"
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_single_rule_invalid_principal_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD, "..", "configs", "manifests", "single_rule_missing_principal_name.yaml"
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_multiple_rules_invalid_principal_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD, "..", "configs", "manifests", "multiple_rules_invalid_principal_type.yaml"
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_single_rule_invalid_rule_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD, "..", "configs", "manifests", "single_rule_invalid_rule_type.yaml"
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_multiple_rule_invalid_rule_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD, "..", "configs", "manifests", "multiple_rules_invalid_rule_type.yaml"
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_single_rule_invalid_target_type_nested_combination() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD,
        "..",
        "configs",
        "manifests",
        "single_rule_invalid_target_type_nested_combination.yaml",
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)


def test_multiple_rules_invalid_target_type_nested_combination() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(
        CWD,
        "..",
        "configs",
        "manifests",
        "multiple_rules_invalid_target_type_nested_combination.yaml",
    )

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        AwsResolver(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)
