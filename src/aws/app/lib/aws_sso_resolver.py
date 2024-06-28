import jsonschema
from utils import load_file

class AwsResolver():
    """ """

    def __init__(
            self,
            manifest_definition_filepath: str,
            schema_definition_filepath: str
        ) -> None:

        self._schema_definition = load_file(schema_definition_filepath)
        self.manifest_definition = load_file(manifest_definition_filepath)

        # validate manifest against schema
        self._is_valid()


    def _is_valid(self) -> None:
        """
        Validates the manifest definition against the schema definition.

        Returns:
        -------
        bool
            True if the manifest is valid, raises jsonschema.ValidationError otherwise.
        """
        try:
            jsonschema.validate(instance=self.manifest_definition, schema=self._schema_definition)
        except jsonschema.ValidationError as e:
            raise jsonschema.ValidationError(f"Validation error: {e.message}")
