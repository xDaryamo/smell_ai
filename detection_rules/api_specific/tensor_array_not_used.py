import ast
from detection_rules.smell import Smell


class TensorArrayNotUsedSmell(Smell):
    """
    Detects the misuse of `tf.constant()` in loops instead of `tf.TensorArray` in TensorFlow.

    Example of code smell:
        tensor = tf.constant([1, 2, 3])
        for i in range(5):
            tensor = tf.concat([tensor, [i]])  # Will cause an error.

    Preferred alternative:
        Use `tf.TensorArray` to grow arrays dynamically in loops.
    """

    def __init__(self):
        super().__init__(
            name="tensor_array_not_used",
            description=(
                "If `tf.constant()` is used to initialize an array and modified in a loop, it may cause errors. "
                "Consider using `tf.TensorArray` for dynamically growing arrays."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        smells = []

        # Check for Tensorflow library
        if not any("tensorflow" in lib for lib in extracted_data["libraries"]):
            return smells

        library_name = extracted_data["library_aliases"].get("tensorflow", None)

        # Traverse the AST
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call):
                if hasattr(node.func, "attr") and node.func.attr == "constant":
                    if (
                        hasattr(node.func.value, "id")
                        and node.func.value.id == library_name
                    ):
                        # Check if any argument is a list, which suggests potential misuse
                        if any(isinstance(arg, ast.List) for arg in node.args):
                            smells.append(
                                self.format_smell(
                                    line=node.lineno,
                                    additional_info=(
                                        "Using `tf.TensorArray` is better for dynamically growing arrays."
                                    ),
                                )
                            )
        return smells
