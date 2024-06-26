"""
Unit tests to test writing regex rules from DDB
"""
import os
import pytest
import jsonschema
from src.app.lib.sso_manifest import SsoManifest

# Globals vars
CWD = os.path.dirname(os.path.realpath(__file__))
MANIFEST_SCHEMA_DEFINITION_FILEPATH = os.path.join(CWD, "..", "..", "src", "app", "schemas", "manifest_schema_definition.json")

# Test cases
def test_missing_rules() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "missing_rules.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_single_rule_invalid_rules_target_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "single_rule_invalid_rules_target_type.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_multiple_rules_invalid_rules_target_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "multiple_rules_invalid_rules_target_type.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_single_rule_invalid_rules_access_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "single_rule_invalid_rules_access_type.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_multiple_rules_invalid_rules_access_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "multiple_rules_invalid_rules_access_type.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_single_rule_missing_permission_set_name() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "single_rule_missing_permission_set_name.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_multiple_rules_missing_permission_set_name() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "multiple_rules_missing_permission_set_name.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_single_rule_missing_principal_name() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "single_rule_missing_principal_name.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_multiple_rules_missing_principal_name() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "multiple_rules_missing_principal_name.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_single_rule_invalid_principal_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "single_rule_missing_principal_name.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_multiple_rules_invalid_principal_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "multiple_rules_invalid_principal_type.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_single_rule_invalid_rule_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "single_rule_invalid_rule_type.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_multiple_rule_invalid_rule_type() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "multiple_rules_invalid_rule_type.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()


def test_single_rule_invalid_target_type_nested_combination() -> None:
    # Arrange
    manifest_definition_filepath = os.path.join(CWD, "..", "configs", "manifests", "single_rule_invalid_target_type_nested_combination.yaml")
    py_sso_manifest = SsoManifest(manifest_definition_filepath, MANIFEST_SCHEMA_DEFINITION_FILEPATH)

    # Assert
    with pytest.raises(jsonschema.ValidationError):
        py_sso_manifest.is_valid()

