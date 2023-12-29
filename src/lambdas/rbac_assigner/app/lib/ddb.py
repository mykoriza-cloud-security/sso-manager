"""
This module contains a Boto3 DynamoDB client to interact with the AWS DynamoDB service

This module consists of the following classes:
    - DDB: DynamoDB client to interact with DDB
"""

import boto3
import beartype

from boto3.dynamodb.conditions import Key, Attr


class DDB:
    """
    Boto3 based DynamoDB client to interact with DDB Database.

    This DDB class consists of three class methods:
        - __init__: default constructor to initialize various class variables
        - batch_put_items: batch writes a list of objects to DDB
        - batch_query_items: batch queries a list of objects from DDB
        - _query_items (private method): private method used to query DDB
    """

    def __init__(self, table_name: str) -> None:
        """
        Default constructor, creates a DDB resource object and establishes
        a client conection to the DDB table to be interacted with

        Parameters
        ----------
            - table_name: str, required
                DDB table name to interact with
        """
        self._ddb_table_hash_key = "pk"
        self._ddb_table_range_key = "sk"
        self._ddb_resource = boto3.resource("dynamodb")
        self._ddb_table = self._ddb_resource.Table(table_name)

    @beartype.beartype
    def batch_put_items(self, items: list[dict]) -> None:
        """
        Boto3 DDB function to batch write list of items to DDB Table

        Parameters
        ----------
        items: list, required
            list of objects to be written to DDB
        """
        with self._ddb_table.batch_writer() as writer:
            for item in items:
                writer.put_item(Item=item)

    # pylint: disable=R0913
    @beartype.beartype
    def batch_query_items(
        self,
        key: str,
        range_begins_with: str = "",
        filter_expression_attribute: str = "",
        filter_expression_value: str = "",
        projection_expression: str = "",
    ) -> list:
        """
        Boto3 DDB function to batch write list of items to DDB Table

        Parameters
        ----------
        key: str, required
            DDB table hash key name

        range_begins_with: str, optional
            Range key string prefix to scope queries

        filter_expression_attribute: str, optional
            Applied after a query is complete but before values are returned, is
            an expression to filter returned results based on desired attribute name

        filter_expression_value: str, optional
            Applied after a query is complete but before values are returned, is
            an expression to filter returned results based on desired attribute value

        projection_expression: str, optional
            Expression to determine what attributes to return for a queried DDB item

        Returns
        -------
        items:
            List of queried DDB objects
        """
        if range_begins_with:
            key_condition = Key(self._ddb_table_hash_key).eq(key) & Key(
                self._ddb_table_range_key
            ).begins_with(range_begins_with)
        else:
            key_condition = Key(self._ddb_table_hash_key).eq(key)

        if filter_expression_attribute and filter_expression_value:
            filter_expression = Attr(filter_expression_attribute).eq(
                filter_expression_value
            )
        else:
            filter_expression = ""

        return [
            item
            for page in self._query_items(
                key_condition, filter_expression, projection_expression
            )
            for item in page
            if page
        ]

    @beartype.beartype
    def _query_items(
        self,
        key_condition: boto3.dynamodb.conditions.And,
        filter_expression: str = "",
        projection_expression: str = "",
    ) -> beartype.typing.Iterator[list]:
        """
        Boto3 DDB function to batch write list of items to DDB Table

        Parameters
        ----------
        key_condition_expression: str, required
            String containing comma separated key value pairs of hash and/or range
            key name & attribute values

        filter_expression_value: str, optional
            String containing comma separated key value pairs of filter
            name & attribute values

        projection_expression: str, optional
            Expression to determine what attributes to return for a queried DDB item

        Returns
        -------
        items:
            List of queried DDB objects
        """
        kwargs = {
            "KeyConditionExpression": key_condition,
            "FilterExpression": filter_expression,
            "ProjectionExpression": projection_expression,
        }
        kwargs = {k: v for k, v in kwargs.items() if v}
        response = self._ddb_table.query(**kwargs)
        yield response.get("Items", [])

        if "ExclusiveStartKey" in response:
            kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        while "ExclusiveStartKey" in response:
            response = self._ddb_table.query(**kwargs)
            yield response.get("Items", [])
