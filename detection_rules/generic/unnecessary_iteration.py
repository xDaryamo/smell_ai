import ast
from detection_rules.smell import Smell


class UnnecessaryIterationSmell(Smell):
    """
    Detects unnecessary iterations over Pandas objects, such as using `iterrows()`.

    Example of code smell:
        for index, row in df.iterrows():
            df["column"] = row["value"]  # Inefficient

    Preferred alternative:
        Use vectorized Pandas operations (e.g., `df["column"] = df["value"]`).
    """

    def __init__(self):
        super().__init__(
            name="unnecessary_iteration",
            description=(
                "Iterating through Pandas objects is generally slow. "
                "Use built-in vectorized methods (e.g., join, groupby) instead of loops."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        smells = []

        # Check for Pandas library
        if not any("pandas" in lib for lib in extracted_data["libraries"]):
            return smells

        dataframe_variables = extracted_data.get("dataframe_variables", [])

        for node in ast.walk(ast_node):
            # Identify `for` loops iterating over `iterrows()`
            if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
                if (
                    isinstance(node.iter.func, ast.Attribute)
                    and node.iter.func.attr == "iterrows"
                    and hasattr(node.iter.func.value, "id")
                    and node.iter.func.value.id in dataframe_variables
                ):
                    # Add loop variables to the DataFrame variable list
                    if isinstance(node.target, ast.Tuple):
                        for target in node.target.elts:
                            if isinstance(target, ast.Name):
                                dataframe_variables.append(target.id)

                    # Check for operations on the DataFrame inside the loop
                    for n in ast.walk(node):
                        op_to_analyze = None
                        if isinstance(n, ast.Call) and isinstance(
                            n.func, ast.Attribute
                        ):
                            if n.func.attr == "append":
                                op_to_analyze = n.args[0] if n.args else None

                        if isinstance(n, ast.Assign):
                            if isinstance(n.value, ast.BinOp):
                                op_to_analyze = n.value

                        if op_to_analyze:
                            left = self._get_base_variable(op_to_analyze.left)
                            right = self._get_base_variable(op_to_analyze.right)

                            if (
                                left in dataframe_variables
                                or right in dataframe_variables
                            ):
                                smells.append(
                                    self.format_smell(
                                        line=node.lineno,
                                        additional_info=(
                                            "Using `iterrows` detected. Consider using vectorized operations instead."
                                        ),
                                    )
                                )
        return smells

    def _get_base_variable(self, node: ast.AST) -> str:
        """
        Recursively retrieves the base variable of a subscript or attribute.

        :param node: The AST node to analyze.
        :return: The base variable name, or None if not found.
        """
        while isinstance(node, ast.Subscript):
            node = node.value
        return node.id if isinstance(node, ast.Name) else None
