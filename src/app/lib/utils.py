"""
Python module consisting of utils functions that are used accross
the various python modules in this repo
"""
import decimal
import logging
import datetime
import functools
import dataclasses
import boto3

LOGGER = logging.getLogger(__name__)


def recursive_process_dict(dict_object: dict):
    """
    Utils function to recursively parse and process dictionary values
    and adjust item source datatypes into target dataypes

    Parameters
    ----------
        - dict_object: dict, required
            Dictionary object to be processed

    Returns
    -------
    dict_object:
        Processed dictionary object
    """
    for k, v in dict_object.items():
        if isinstance(v, dict):
            recursive_process_dict(v)
        else:
            if isinstance(v, (int, float)):
                dict_object[k] = decimal.Decimal(v)
            elif isinstance(v, decimal.Decimal):
                dict_object[k] = float(v)
            elif isinstance(v, datetime.datetime):
                dict_object[k] = v.strftime("%y-%m-%d %H:%M:%S")
            else:
                continue
    return dict_object


def handle_aws_sso_errors(func):
    """
    Decorator functions that acts on or return passed function

    Parameters
    ----------
        - func: required
    """

    @functools.wraps(func)
    # pylint: disable=C0116
    # pylint: disable=R1710
    def execute_function_safely(*args, **kwargs):
        # pylint: disable=R0911
        """Function to execute passed in function, or capture exceptions
        and return error message and code based on exception type

        Returns
        -------
        func:
            safely executed function
        """
        # pylint: disable=W0718
        # pylint: disable=R1705
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if type(e).__name__ == "ConflictException":
                LOGGER.error(e)
                return "Permission set already exists", 400
            elif type(e).__name__ == "AccessDeniedException":
                LOGGER.error(e)
                return "Insufficient permissions to perform task", 400
            elif type(e).__name__ == "InternalServerException":
                LOGGER.error(e)
                return "Internal server error, check application logs", 500
            elif type(e).__name__ == "ResourceNotFoundException":
                LOGGER.error(e)
                return "Specified resource doesn't exist", 400
            elif type(e).__name__ == "ThrottlingException":
                LOGGER.error(e)
                return "Invalid input parameters", 400
            elif type(e).__name__ == "ValidationException":
                LOGGER.error(e)
                return "Syntax error", 400

    return execute_function_safely


def generate_lambda_context():
    """
    Utils function to create lambda context object instance

    Returns
    -------
    LambdaContext:
        Dataclass object to AWS Lambda context
    """

    @dataclasses.dataclass
    class LambdaContext:
        """
        Creates an AWS Lambda context class. This class's attributes
        consists of the following mock attributes:

            - function_name: str, default: test
            - function_version: str, default: $LATEST
            - invoked_function_arn: str, default: \
                arn:aws:lambda:us-east-1:123456789101:function:test
            - memory_limit_in_mb: int, default: 256
            - aws_request_id: str, default: 810d00ae-669c-4100-88dd-334888a04cc2
            - log_group_name: str, default: /aws/lambda/test
            - log_stream_name: str, default: my-log-stream
        """

        function_name: str = "test"
        function_version: str = "$LATEST"
        invoked_function_arn: str = (
            f"arn:aws:lambda:us-east-1:123456789101:function:{function_name}"
        )
        memory_limit_in_mb: int = 256
        aws_request_id: str = "810d00ae-669c-4100-88dd-334888a04cc2"
        log_group_name: str = f"/aws/lambda/{function_name}"
        log_stream_name: str = "my-log-stream"

        def get_remaining_time_in_millis(self) -> int:
            """Return mock remaining time in milli seconds for lambda"""
            return 5

    return LambdaContext()


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
