import ast
from detection_rules.smell import Smell


class DataFrameConversionAPIMisused(Smell):
    """
    Detects the misuse of the `values` attribute in Pandas DataFrames.

    Example of code smell:
        df.values  # Deprecated, unclear return type

    Preferred alternative:
        Use NumPy arrays or other Pandas methods for conversion.
    """

    def __init__(self):
        super().__init__(
            name="dataframe_conversion_api_misused",
            description="Using the `values` attribute in Pandas is deprecated. Use NumPy or explicit methods instead.",
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        """
        Detects misuse of the `values` attribute in DataFrames.

        Parameters:
        - ast_node (ast.AST): The root AST node of the file being analyzed.
        - extracted_data (dict[str, any]): A dictionary containing preprocessed information from the code.
        - filename (str): The name of the file being analyzed.

        Returns:
        - list[dict[str, any]]: A list of detected smells, each represented as a dictionary.
        """
        smells = []

        # Ensure the Pandas library is used
        pandas_alias = extracted_data["libraries"].get("pandas")
        if not pandas_alias:
            return smells

        dataframe_variables = extracted_data.get("dataframe_variables", [])
        lines = extracted_data.get("lines", {})

        # Traverse the AST
        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "values"  # Check for the `values` attribute
                and isinstance(node.value, ast.Name)
                and node.value.id in dataframe_variables
            ):
                # Extract the offending line for additional context
                code_snippet = lines.get(node.lineno, "<Code not available>")
                smells.append(
                    self.format_smell(
                        line=node.lineno,
                        additional_info=(
                            f"Misuse of the 'values' attribute detected in variable '{node.value.id}'. "
                            "Please consider using NumPy or explicit methods instead of `values` for DataFrame conversion. "
                            "The function 'values' is deprecated and its return type is unclear. "
                            f"Code: {code_snippet}"
                        ),
                    )
                )

        return smells
