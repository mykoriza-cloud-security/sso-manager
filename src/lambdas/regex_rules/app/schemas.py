"""Schemas module to define Regex Rules microservice event schema"""
from typing import List, Optional
from aws_lambda_powertools.utilities.parser import BaseModel


class RegexRulesModel(BaseModel):  # pylint: disable=R0903
    """Class to define Regex Rules microservice event schema"""

    regex_rules: Optional[List[Optional[str]]]
