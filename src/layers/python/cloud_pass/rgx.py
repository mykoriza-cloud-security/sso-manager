"""This module contains Regex based rules engine to process regular expression string inputs.
"""
import re


# pylint: disable=R0903
class RGX:
    """Regex based rules engine to process regular expression string inputs.

    This class consists of the following class methods:
        - is_valid_regex: checks if input string is a valid regex expression
    """

    def is_valid_regex(self, regex_string: str) -> bool:
        """Check if input string is a valid regex expression

        Parameters
        ----------
            - regex_string: str, required
                Input regex string

        Returns
        -------
        boolean:
            Boolean value if regex is valid or not
        """
        try:
            re.compile(regex_string)
            return True
        except re.error:
            return False
