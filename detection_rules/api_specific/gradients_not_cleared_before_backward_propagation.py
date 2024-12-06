import ast
from detection_rules.smell import Smell


class GradientsNotClearedSmell(Smell):
    """
    Detects cases where gradients are not cleared before backward propagation in PyTorch.

    Example of code smell:
        optimizer.backward()  # Missing zero_grad() before backward()

    Preferred alternative:
        optimizer.zero_grad()
        optimizer.backward()  # Proper sequence
    """

    def __init__(self):
        super().__init__(
            name="gradients_not_cleared_before_backward_propagation",
            description="Gradients must be cleared using `zero_grad()` before calling `backward()`.",
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        smells = []

        # Check for Torch library
        if not any("torch" in lib for lib in extracted_data["libraries"]):
            return smells

        for node in ast.walk(ast_node):
            # Check for loops (for/while) where gradients might be updated
            if isinstance(node, (ast.For, ast.While)):
                zero_grad_called = False
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call) and hasattr(subnode.func, "attr"):
                        # Detect `zero_grad` calls
                        if subnode.func.attr == "zero_grad":
                            zero_grad_called = True
                        # Detect `backward` calls
                        if subnode.func.attr == "backward" and not zero_grad_called:
                            smells.append(
                                self.format_smell(
                                    line=subnode.lineno,
                                    additional_info="Please consider to use zero_grad() before backward().",
                                )
                            )
        return smells
