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
        smells = []

        # Check for Torch library
        if not any("torch" in lib for lib in extracted_data["libraries"]):
            return smells

        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Call)
                and hasattr(node.func, "attr")
                and node.func.attr == "forward"
            ):
                if (
                    hasattr(node.func, "value")
                    and hasattr(node.func.value, "id")
                    and node.func.value.id == "self"
                ):
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info="Direct call to `self.forward()` detected. Use the model instance instead.",
                        )
                    )
        return smells
