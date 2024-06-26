import json
import yaml
import jsonschema

class SsoManifest:
    """
    A class to represent and validate an SSO Manifest.

    Attributes:
    ----------
    _manifest_definition : dict
        The manifest file content.
    _schema_definition : dict
        The schema definition to validate the manifest file against.

    Methods:
    -------
    is_valid():
        Validates the manifest file against the schema definition.
    """

    def __init__(self, manifest_definition_filepath: str, schema_definition_filepath: str) -> None:
        """
        Initializes the SsoManifest with a manifest definition and a schema definition.

        Parameters:
        ----------
        manifest_definition_filepath : str
            Path to the YAML manifest definition file.
        schema_definition_filepath : str
            Path to the JSON schema definition file.
        """
        self._manifest_definition = self._load_yaml_file(manifest_definition_filepath)
        self._schema_definition = self._load_json_file(schema_definition_filepath)

    def _load_yaml_file(self, filepath: str) -> dict:
        """Loads a YAML file and returns its content as a dictionary."""
        with open(filepath, "r") as file:
            return self._convert_strings_to_lowercase(yaml.safe_load(file))

    def _load_json_file(self, filepath: str) -> dict:
        """Loads a JSON file and returns its content as a dictionary."""
        with open(filepath, "r") as file:
            return json.load(file)
    
    def _convert_strings_to_lowercase(self, item):
        """
        Recursively traverse a dictionary and convert all string values to lowercase.

        :param d: Dictionary to be processed
        :return: Dictionary with all string values converted to lowercase
        """
        if isinstance(item, dict):
            return {k: self._convert_strings_to_lowercase(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [self._convert_strings_to_lowercase(item) for item in item]
        elif isinstance(item, str):
            return item.lower()
        else:
            return item

    def is_valid(self) -> None:
        """
        Validates the manifest definition against the schema definition.

        Returns:
        -------
        bool
            True if the manifest is valid, raises jsonschema.ValidationError otherwise.
        """
        try:
            jsonschema.validate(instance=self._manifest_definition, schema=self._schema_definition)
        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"Validation error: {e.message}")
