"""Module containing utils variables & functions for sister testing modules"""

# Global vars
COMMON_ERROR_MESSAGES = {
    "list_size": "Expected different list size",
    "http_status_code": "Unexpected HTTP status code",
    "response_message": "Unexpected response message",
    "regex_pattern": "Item does not match expected Regex pattern",
    "ddb_numerical": "Incorrect numerical DynamoDB item datatype",
    "hash_key": "Processed hash key name is different from desired",
    "expected_keys": "Returned dictionary keys different from expected",
}
