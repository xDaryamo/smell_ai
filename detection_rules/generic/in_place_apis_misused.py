import ast
from detection_rules.smell import Smell


class InPlaceAPIsMisusedSmell(Smell):
    """
    Detects cases where Pandas in-place APIs are used incorrectly, potentially causing confusion about memory usage.

    Example of code smell:
        df.drop(columns=["column_name"], inplace=False)  # Potential misuse

    Preferred alternative:
        Use either:
        - df = df.drop(columns=["column_name"])  # Assign result to a variable
        - df.drop(columns=["column_name"], inplace=True)  # Explicitly use in-place operation
    """

    def __init__(self):
        super().__init__(
            name="in_place_apis_misused",
            description=(
                "Check whether the result of the operation is assigned to a variable or the in-place parameter is set. "
                "Some developers mistakenly assume in-place operations always save memory."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:

        smells = []

        # Check for Pandas library
        if not any("pandas" in lib for lib in extracted_data["libraries"]):
            return smells

        dataframe_methods = extracted_data.get("dataframe_methods", [])
        dataframe_variables = extracted_data.get("dataframe_variables", [])

        # Traverse AST nodes
        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
            ):
                # Ensure the method is applied on a DataFrame variable
                if (
                    hasattr(node.value.func.value, "id")
                    and node.value.func.value.id in dataframe_variables
                    and node.value.func.attr in dataframe_methods
                ):
                    # Check for the "inplace" parameter
                    inplace_flag = False
                    for keyword in getattr(node.value, "keywords", []):
                        if (
                            keyword.arg == "inplace"
                            and getattr(keyword.value, "value", None) is True
                        ):
                            inplace_flag = True

                    # If "inplace" is not set, flag it as a smell
                    if not inplace_flag:
                        smells.append(
                            self.format_smell(
                                line=node.lineno,
                                additional_info=(
                                    "We suggest developers check whether the result of the operation is assigned to a variable "
                                    "or the in-place parameter is set explicitly."
                                ),
                            )
                        )

        return smells
