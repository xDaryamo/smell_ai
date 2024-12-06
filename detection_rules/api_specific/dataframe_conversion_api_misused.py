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
        smells = []

        # Check for Pandas library
        if not any("pandas" in lib for lib in extracted_data["libraries"]):
            return smells

        dataframe_variables = extracted_data.get("dataframe_variables", [])

        # Traverse the AST
        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "values"  # Check for the `values` attribute
                and hasattr(node.value, "id")
                and node.value.id in dataframe_variables
            ):
                smells.append(
                    self.format_smell(
                        line=node.lineno,
                        additional_info=(
                            "Please consider using numpy or explicit methods instead of `values` for DataFrame conversion. "
                            "The function 'values' is deprecated and its return type is unclear."
                        ),
                    )
                )

        return smells
