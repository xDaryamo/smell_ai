import ast
from detection_rules.smell import Smell


class MemoryNotFreedSmell(Smell):
    """
    Detects cases where memory is not freed in TensorFlow, such as not calling `tf.keras.backend.clear_session()`
    inside loops where models are defined.

    Example of code smell:
        for i in range(10):
            model = build_model()  # Define model in a loop
            # Missing tf.keras.backend.clear_session()

    Preferred alternative:
        for i in range(10):
            model = build_model()
            tf.keras.backend.clear_session()  # Free memory explicitly
    """

    def __init__(self):
        super().__init__(
            name="memory_not_freed",
            description=(
                "Memory not freed after model definition in loops may lead to memory leakage. "
                "Consider using `tf.keras.backend.clear_session()` to free memory explicitly."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:

        smells = []

        # Check for Tensorflow library
        tensorflow_alias = extracted_data["library_aliases"].get("tensorflow", None)
        if not tensorflow_alias:
            return smells

        model_methods = extracted_data.get("model_methods", [])
        for_loop_nodes = [
            node
            for node in ast.walk(ast_node)
            if isinstance(node, (ast.For, ast.While))
        ]

        for loop_node in for_loop_nodes:
            model_defined = False
            memory_freed = False

            # Check if a TensorFlow model method is called within the loop
            for n in ast.walk(loop_node):
                if (
                    isinstance(n, ast.Call)
                    and hasattr(n.func, "attr")
                    and n.func.attr in model_methods
                    and hasattr(n.func.value, "id")
                    and n.func.value.id == tensorflow_alias
                ):
                    model_defined = True

            # Check if memory is freed using `clear_session`
            if model_defined:
                for n in ast.walk(loop_node):
                    if (
                        isinstance(n, ast.Call)
                        and hasattr(n.func, "attr")
                        and n.func.attr == "clear_session"
                        and hasattr(n.func.value, "id")
                        and n.func.value.id == tensorflow_alias
                    ):
                        memory_freed = True
                        break

            # Report a smell if memory is not freed
            if model_defined and not memory_freed:
                smells.append(
                    self.format_smell(
                        line=loop_node.lineno,
                        additional_info=(
                            "Memory not freed after model definition in loop. "
                            "Consider using `tf.keras.backend.clear_session()`."
                        ),
                    )
                )

        return smells
