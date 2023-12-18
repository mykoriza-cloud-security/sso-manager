"""Module to run test cases against DynamoDB python client"""
# Imports
import unittest
import moto

# Local package imports
from cloud_pass.ddb import DDB
from cloud_pass.utils import (
    create_table,
    delete_table,
)

# Globals
DDB_TABLE_NAME = "cloud_pass"


@moto.mock_dynamodb
class TestDDB(unittest.TestCase):
    """Class to run test cases against DynamoDB python client"""

    def setUp(self) -> None:
        """Creates DDB table, writes sample data to DDB table, and
        lambda context prior to test case execution
        """
        create_table(table_name=DDB_TABLE_NAME, secondary_key="sk")

    def tearDown(self) -> None:
        """Delete DDB table after test case execution"""
        delete_table(DDB_TABLE_NAME)

    ##################################
    #            Test Cases          #
    ##################################

    def test_ddb_table_name_not_null(self) -> None:
        """Test case to check if DDB table name is not null and a class instance
        is defined with a table
        """
        with self.assertRaises(ValueError, msg="DDB table name must be defined"):
            DDB(table_name=None)
