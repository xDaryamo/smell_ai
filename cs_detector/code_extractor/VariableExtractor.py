import re
import ast

class VariableExtractor:
    def __init__(self) -> None:
        self.set_variables = set()

    def get_variable_def(self, line: str) -> str:
        """
        Extracts the variable definition from a single line of code.
        """
        pattern = r'(\w)+(\[.*\])+\s*=\s*(\w*)'
        if re.match(pattern, line):
            variable = line.split('=')[0].strip().split('[')[0].strip()
            return variable
        return None

    def get_all_set_variables(self, lines: list[str]) -> set[str]:
        """
        Extracts and stores all set variables from a list of lines.
        """
        for line in lines:
            variable = self.get_variable_def(line)
            if variable:
                self.set_variables.add(variable)
        return self.set_variables

    def search_variable_definition(self, var: str, fun_node: any, limit_node: any) -> any:
        """
        Searches for a variable's last definition within a function node, up to a limit node.
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

    def equal_node(self, node1: any, node2: any) -> bool:
        """
        Compares two AST nodes for equality.
        """
        return (hasattr(node1, 'lineno') and hasattr(node2, 'lineno') and
                node1.lineno == node2.lineno and node1.col_offset == node2.col_offset)
