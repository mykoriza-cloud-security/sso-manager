"""Schemas module to define Regex Rules microservice event schema"""
from typing import List, Optional
from aws_lambda_powertools.utilities.validation import SchemaValidationError
from aws_lambda_powertools.utilities.parser import parse, BaseModel, validator

class RegexRulesModel(BaseModel):  # pylint: disable=R0903
    """Class to define Regex Rules microservice event schema"""
    regex_rules: List[Optional[str]]
