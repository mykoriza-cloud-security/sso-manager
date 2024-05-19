import os
from abc import ABC, abstractmethod

class BaseResolver(ABC):
    """
    """

    @abstractmethod
    def _is_explicit_assignment(self):
        """
        """
        pass
    
    @abstractmethod
    def _is_expired(self):
        """
        """
        pass

    @abstractmethod
    def create_assignments_mapping(self):
        """
        """
        pass

class RbacResolver(BaseResolver):
    """
    """

    def __init__(self) -> None:
        super().__init__()
        self._assignment_rules_delimiters = [x.strip() for x in os.getenv("ASSIGNMENT_RULES_DELIMITERS", "@, :, =, #")]

    
    def _is_explicit_assignment(self, assignment_rule):
        """
        """
        return any(
            self._contains_rule_delimiter(assignment_rule)
        )
        

    def _is_expired(self):
        """
        """
        pass


    def create_assignments_mapping(
            self,
            aws_accounts=list[dict],
            sso_groups=list[dict],
            permission_sets=list[dict],
            assignment_rules=list[dict]
    ) -> list[dict]:
        """
        """
        for rule in assignment_rules:
            if self._is_explicit_assignment(rule):
                pass
                # split rule string into sso_group and targets
                sso_group, targets = rule.split(self._assignment_rules_delimiters)
                # check if targrets have comma delimiters too and split those
                targets = targets.split(",")
                # create a mapping of sso_group to targets
                for target in targets:
                    # Check if account or organizational unit
                    is_account = None             # regex -> account ID
                    is_organizational_unit = None # regex -> ou ID or root out ID

            else:
                pass

        

    def _contains_rule_delimiter(self, rbac_rule):
        """
        Checks if any character in the given delimiter list
        is present in the input rbac_rule string.
        
        Args:
            input_str (str): The input string to check.
            char_list (list): A list of characters to search for.
        
        Returns:
            bool: True if any character in the list is found in the input string, False otherwise.
        """
        return any(char in rbac_rule for char in self._assignment_rules_delimiters)
