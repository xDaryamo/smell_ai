import re
import ast

class VariableExtractor:
    def __init__(self):
        """
        Initializes the VariableExtractor.

        Instance Variables:
        - self.set_variables (set[str]): A set of variables that have been extracted and stored.
        """
        self.set_variables = set()

    def get_variable_def(self, line: str) -> str:
        """
        Extracts the variable name from a single line of code.

        Parameters:
        - line (str): A line of code to analyze for variable definitions.

        Returns:
        - str: The name of the variable being defined in the line.
               Returns None if no variable definition is found.

        Notes:
        - This method uses a regex pattern to identify variable definitions of the form `variable_name[...] = value`.
        """
        pattern = r'(\w)+(\[.*\])+\s*=\s*(\w*)'
        if re.match(pattern, line):
            variable = line.split('=')[0].strip().split('[')[0].strip()
            return variable
        return None

    def get_all_set_variables(self, lines: list[str]) -> set[str]:
        """
        Extracts and stores all set variables from a list of lines of code.

        Parameters:
        - lines (list[str]): A list of lines of code to analyze for variable definitions.

        Returns:
        - set[str]: A set of all variable names that were identified and stored.

        Notes:
        - This method iterates over each line, uses `get_variable_def` to extract variables,
          and adds them to the `self.set_variables` set.
        """
        for line in lines:
            variable = self.get_variable_def(line)
            if variable:
                self.set_variables.add(variable)
        return self.set_variables

    def search_variable_definition(self, var: str, fun_node: ast.AST, limit_node: ast.AST) -> ast.AST:
        """
        Searches for the last definition of a variable within a function node, up to a limit node.

        Parameters:
        - var (str): The name of the variable to search for.
        - fun_node (ast.AST): The AST node representing the function to analyze.
        - limit_node (ast.AST): The AST node that serves as a stopping point for the search.

        Returns:
        - ast.AST: The AST node representing the last definition of the variable, or None if not found.

        Notes:
        - The search stops when the `limit_node` is reached.
        - This method specifically looks for `ast.Assign` nodes where the target matches the variable name.
        """
        last_node_definition = None
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == var:
                        last_node_definition = node
            if self.equal_node(node, limit_node):
                return last_node_definition
        return last_node_definition

    def equal_node(self, node1: ast.AST, node2: ast.AST) -> bool:
        """
        Compares two AST nodes for equality based on their line number and column offset.

        Parameters:
        - node1 (ast.AST): The first AST node to compare.
        - node2 (ast.AST): The second AST node to compare.

        Returns:
        - bool: True if the nodes have the same `lineno` and `col_offset` attributes; False otherwise.

        Notes:
        - This method assumes that both nodes have `lineno` and `col_offset` attributes.
        - If either node lacks these attributes, the method returns False.
        """
        return (hasattr(node1, 'lineno') and hasattr(node2, 'lineno') and
                node1.lineno == node2.lineno and node1.col_offset == node2.col_offset)
