import ast
from detection_rules.smell import Smell


class MergeAPIParameterNotExplicitlySetSmell(Smell):
    """
    Detects cases where Pandas' `merge` API is called without explicitly setting important parameters.

    Example of code smell:
        df1.merge(df2)  # Missing 'how', 'on', or 'validate' parameters.

    Preferred alternative:
        df1.merge(df2, how='inner', on='key', validate='one_to_one')
    """

    def __init__(self):
        super().__init__(
            name="merge_api_parameter_not_explicitly_set",
            description=(
                "Calls to Pandas' `merge` API should explicitly set parameters like 'how', 'on', and 'validate' "
                "to avoid unexpected behavior."
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

        # Traverse AST nodes
        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Call)
                and hasattr(node.func, "attr")
                and node.func.attr == "merge"
            ):
                # Check if the method is applied on a DataFrame variable
                if (
                    hasattr(node.func.value, "id")
                    and node.func.value.id in dataframe_variables
                ):
                    # Check for missing or incomplete parameters
                    if not hasattr(node, "keywords") or node.keywords is None:
                        smells.append(
                            self.format_smell(
                                line=node.lineno,
                                additional_info="Missing explicit parameters in `merge` (e.g., 'how', 'on', 'validate').",
                            )
                        )
                    else:
                        args = [x.arg for x in node.keywords]
                        if not {"how", "on", "validate"}.issubset(set(args)):
                            smells.append(
                                self.format_smell(
                                    line=node.lineno,
                                    additional_info="Incomplete parameters in `merge` (e.g., 'how', 'on', 'validate').",
                                )
                            )

        return smells
