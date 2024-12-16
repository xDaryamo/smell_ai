import ast
from detection_rules.smell import Smell


class EmptyColumnMisinitializationSmell(Smell):
    """
    Detects cases where Pandas DataFrame columns are initialized
    with zero or empty strings, which can cause issues with methods
    like .isnull() or .notnull().

    Example of code smell:
        df["new_column"] = 0  # Incorrect
        df["new_column"] = ""  # Incorrect

    Preferred alternative:
        df["new_column"] = np.nan
        # Use NaN for better handling of empty values.
    """

    def __init__(self):
        super().__init__(
            name="empty_column_misinitialization",
            description=(
                "Using zeros or empty strings to initialize "
                "new DataFrame columns may cause issues. "
                "Consider using NaN (e.g., np.nan) instead."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        # Ensure Pandas library is used
        pandas_alias = extracted_data["libraries"].get("pandas")
        if not pandas_alias:
            return smells

        dataframe_variables = extracted_data.get("dataframe_variables", [])

        # Traverse AST to find DataFrame column assignments
        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Assign)  # An assignment statement
                and len(node.targets) == 1  # Single assignment target
                and isinstance(
                    node.targets[0], ast.Subscript
                )  # Accessing a DataFrame column (e.g., df["col"])
                and isinstance(
                    node.targets[0].value, ast.Name
                )  # Base variable (e.g., df)
                and node.targets[0].value.id
                in dataframe_variables  # Variable is a known DataFrame
            ):
                # Check the assigned value
                assigned_value = node.value
                if isinstance(
                    assigned_value, ast.Constant
                ) and assigned_value.value in {0, "", ""}:
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                f"Column '{node.targets[0].slice.value}' "
                                f"in DataFrame '{node.targets[0].value.id}' "
                                "is initialized with a zero or empty string. "
                                "Consider using NaN instead."
                            ),
                        )
                    )

        return smells
