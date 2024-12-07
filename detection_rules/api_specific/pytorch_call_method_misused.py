import ast
from detection_rules.smell import Smell


class PyTorchCallMethodMisusedSmell(Smell):
    """
    Detects misuse of the `forward` method in PyTorch models.

    Example of code smell:
        self.forward(x)  # Direct call to forward() is discouraged.

    Preferred alternative:
        self.net(x)  # Use the model's instance directly.
    """

    def __init__(self):
        super().__init__(
            name="pytorch_call_method_misused",
            description="Direct calls to `forward` in PyTorch models are discouraged. Use the model instance directly.",
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        """
        Detects misuse of the `forward` method in PyTorch models.

        Parameters:
        - ast_node (ast.AST): The root AST node of the file being analyzed.
        - extracted_data (dict[str, any]): A dictionary containing preprocessed information from the code.
        - filename (str): The name of the file being analyzed.

        Returns:
        - list[dict[str, any]]: A list of detected smells, each represented as a dictionary.
        """
        smells = []

        # Ensure PyTorch library is used
        torch_alias = extracted_data["libraries"].get("torch")
        if not torch_alias:
            return smells

        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "forward"
            ):
                # Detect direct calls to `forward()` on `self` or other objects
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id in extracted_data["variables"]
                ):
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                f"Direct call to `{node.func.value.id}.forward()` detected. "
                                f"Use the model instance directly instead."
                            ),
                        )
                    )
        return smells
