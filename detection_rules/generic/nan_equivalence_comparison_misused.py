import ast
from detection_rules.smell import Smell


class NanEquivalenceComparisonMisusedSmell(Smell):
    """
    Detects cases where NumPy's NaN values are compared directly using equivalence operators,
    which is incorrect as NaN is not equivalent to itself.

    Example of code smell:
        if np.nan == value:  # Incorrect
        if value != np.nan:  # Incorrect

    Preferred alternative:
        Use NumPy functions like np.isnan() for proper NaN checks:
        if np.isnan(value):  # Correct
    """

    def __init__(self):
        super().__init__(
            name="nan_equivalence_comparison_misused",
            description=(
                "Direct equivalence comparisons with NaN should be avoided. "
                "Use functions like np.isnan() instead."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:

        smells = []

        # Check for Numpy library
        if "numpy" not in extracted_data["libraries"]:
            return smells

        library_name = extracted_data["library_aliases"].get("numpy", None)
        if not library_name:
            return smells

        # Traverse the AST nodes
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Compare):
                nan_equivalence = False

                # Check if the left-hand side involves np.nan
                if (
                    isinstance(node.left, ast.Attribute)
                    and node.left.attr == "nan"
                    and getattr(node.left.value, "id", None) == library_name
                ):
                    nan_equivalence = True

                # Check if any comparator involves np.nan
                for expr in node.comparators:
                    if (
                        isinstance(expr, ast.Attribute)
                        and expr.attr == "nan"
                        and getattr(expr.value, "id", None) == library_name
                    ):
                        nan_equivalence = True

                if nan_equivalence:
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                "Direct equivalence comparison with NaN detected. Use np.isnan() instead."
                            ),
                        )
                    )

        return smells
