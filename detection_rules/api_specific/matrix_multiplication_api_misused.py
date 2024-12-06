import ast
from detection_rules.smell import Smell


class MatrixMultiplicationAPIMisused(Smell):
    """
    Detects misuse of the `dot()` function for matrix multiplication in NumPy.

    Example of code smell:
        np.dot([[1, 2], [3, 4]], [[5, 6], [7, 8]])  # Deprecated usage

    Preferred alternative:
        np.matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]])  # Explicit and recommended
    """

    def __init__(self):
        super().__init__(
            name="matrix_multiplication_api_misused",
            description="Using `dot()` for matrix multiplication is discouraged. Use `np.matmul` instead.",
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        smells = []

        # Check for Numpy library
        if not any("numpy" in lib for lib in extracted_data["libraries"]):
            return smells

        library_name = extracted_data["library_aliases"].get("numpy", None)
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call):
                # Check for calls to `dot` in NumPy
                if hasattr(node.func, "attr") and node.func.attr == "dot":
                    if (
                        hasattr(node.func.value, "id")
                        and node.func.value.id == library_name
                    ):
                        # Check the arguments of the `dot()` call
                        matrix_multiplication = self._is_matrix_multiplication(
                            node, extracted_data
                        )
                        if matrix_multiplication:
                            smells.append(
                                self.format_smell(
                                    line=node.lineno,
                                    additional_info="Please consider to use np.matmul to multiply matrix. The function dot() does not return a scalar value, "
                                    "but a matrix.",
                                )
                            )
        return smells

    def _is_matrix_multiplication(
        self, node: ast.Call, extracted_data: dict[str, any]
    ) -> bool:
        """
        Checks if the arguments of a `dot()` function call represent matrices.

        :param node: The AST node of the `dot()` function call.
        :param extracted_data: Dictionary of pre-extracted data.
        :return: True if matrix multiplication is detected, False otherwise.
        """
        if not hasattr(node, "args") or len(node.args) < 2:
            return False

        for arg in node.args:
            # Case 1: Check if the argument is a matrix (list of lists)
            if isinstance(arg, ast.List):
                if all(isinstance(el, ast.List) for el in arg.elts):
                    return True
            # Case 2: Check if the argument is in the list of variables
            elif isinstance(arg, ast.Name) and arg.id in extracted_data["variables"]:
                # Assuming the extracted_data contains all variables as a list without differentiation
                return True

        return False
