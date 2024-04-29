import boto3

"""Module containing utils variables & functions for sister testing modules"""

# Global vars
COMMON_ERROR_MESSAGES = {
    "list_size": "Expected different list size",
    "regex_pattern": "Item does not match expected Regex pattern",
    "ddb_numerical": "Incorrect numerical DynamoDB item datatype",
    "hash_key": "Processed hash key name is different from desired",
    "expected_keys": "Returned dictionary keys different from expected",
}



def create_table(
    table_name: str, primary_key: str = "pk", secondary_key: str = ""
) -> None:
    """
    Create DDB table

    Parameters
    ----------

        - table_name: str, required
            name of DynamoDB table
    """
    ddb_client = boto3.client("dynamodb")
    key_schema = [{"AttributeName": primary_key, "KeyType": "HASH"}]
    attribute_definitions = [{"AttributeName": primary_key, "AttributeType": "S"}]

    if secondary_key:
        seconday_key_schema = {"AttributeName": secondary_key, "KeyType": "RANGE"}
        seconday_attribute_definition = {
            "AttributeName": secondary_key,
            "AttributeType": "S",
        }
        key_schema.append(seconday_key_schema)
        attribute_definitions.append(seconday_attribute_definition)

    ddb_client.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        BillingMode="PAY_PER_REQUEST",
    )


def delete_table(table_name: str) -> None:
    """
    Delete target DDB table

    Parameters
    ----------

        - table_name: str, required
            name of DynamoDB table
    """
    ddb_client = boto3.client("dynamodb")
    ddb_client.delete_table(TableName=table_name)
