import ast
from detection_rules.smell import Smell


class HyperparametersNotExplicitlySetSmell(Smell):
    """
    Detects cases where hyperparameters are not explicitly set when defining models.

    Example of code smell:
        model = Model()  # No hyperparameters set

    Preferred alternative:
        model = Model(hyperparameter=value)  # Explicitly set hyperparameters
    """

    def __init__(self):
        super().__init__(
            name="hyperparameters_not_explicitly_set",
            description=(
                "Hyperparameters should be explicitly set when defining models to ensure clarity and reproducibility."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        smells = []

        # Ensure relevant libraries are imported
        model_libs = extracted_data.get("model_methods", [])
        if not model_libs:
            return smells

        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call):
                method_name = self._extract_method_name(node)

                # Check if the method belongs to model libraries
                if method_name in model_libs:
                    # Check if hyperparameters are explicitly set
                    if not node.args and not getattr(node, "keywords", None):
                        smells.append(
                            self.format_smell(
                                line=node.lineno,
                                additional_info="Hyperparameters not explicitly set for model definition.",
                            )
                        )
        return smells

    def _extract_method_name(self, node: ast.Call) -> str:
        """
        Extracts the method name from an AST Call node.

        :param node: The AST node representing a function or method call.
        :return: The method name as a string.
        """
        while isinstance(node.func, ast.Call):
            node = node.func
        if isinstance(node.func, ast.Attribute):
            return f"{node.func.attr}()"
        if hasattr(node.func, "id"):
            return f"{node.func.id}()"
        return ""
