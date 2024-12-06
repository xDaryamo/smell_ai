import ast
from detection_rules.smell import Smell


class DeterministicAlgorithmOptionSmell(Smell):
    """
    Detects the use of `torch.use_deterministic_algorithms(True)` in PyTorch, which may cause performance issues.

    Example of code smell:
        torch.use_deterministic_algorithms(True)  # Potential performance bottleneck

    Preferred alternative:
        Avoid using this option unless determinism is strictly required.
    """

    def __init__(self):
        super().__init__(
            name="deterministic_algorithm_option_not_used",
            description=(
                "Using `torch.use_deterministic_algorithms(True)` can cause performance issues. "
                "Avoid using this option unless determinism is strictly required."
            ),
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
                and hasattr(node.func, "id")
                and node.func.id == "use_deterministic_algorithms"
            ):
                if (
                    len(node.args) == 1
                    and hasattr(node.args[0], "value")
                    and node.args[0].value == True
                ):
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info="Using `torch.use_deterministic_algorithms(True)` detected. Avoid for performance.",
                        )
                    )
        return smells
