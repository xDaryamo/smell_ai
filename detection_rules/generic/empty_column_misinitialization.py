import ast
import re
from detection_rules.smell import Smell


class EmptyColumnMisinitializationSmell(Smell):
    """
    Detects cases where Pandas DataFrame columns are initialized with zero or empty strings,
    which can cause issues with methods like .isnull() or .notnull().

    Example of code smell:
        df["new_column"] = 0  # Incorrect
        df["new_column"] = ""  # Incorrect

    Preferred alternative:
        df["new_column"] = np.nan  # Use NaN for better handling of empty values.
    """

    def __init__(self):
        super().__init__(
            name="empty_column_misinitialization",
            description=(
                "Using zeros or empty strings to initialize new DataFrame columns may cause issues. "
                "Consider using NaN (e.g., np.nan) instead."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:

        smells = []

        # Check for Pandas library
        if not any("pandas" in lib for lib in extracted_data["libraries"]):
            return smells

        # Extract relevant data
        variables = extracted_data.get("dataframe_variables", [])
        lines = extracted_data.get("lines", {})
        empty_values = {"0", "''", '""'}

        # Traverse AST nodes
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Assign) and node.targets:
                # Check if target is a DataFrame variable
                if (
                    isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id in variables
                ):
                    # Retrieve the corresponding line of code
                    line = lines.get(node.lineno - 1, "")
                    pattern = rf"{re.escape(node.targets[0].id)}\[\s*.*\s*\]"

                    # Check if the assignment matches the pattern
                    if re.match(pattern, line):
                        assigned_value = line.split("=", 1)[
                            1
                        ].strip()  # Split on first '='
                        if assigned_value in empty_values:
                            smells.append(
                                self.format_smell(
                                    line=node.lineno,
                                    additional_info=(
                                        "Avoid using zeros or empty strings to initialize DataFrame columns. "
                                        "Use NaN instead."
                                    ),
                                )
                            )
        return smells
