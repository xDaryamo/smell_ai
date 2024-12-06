import ast
from detection_rules.smell import Smell


class ChainIndexingSmell(Smell):
    """
    Detects the use of chained indexing in Pandas DataFrames.

    Example of chained indexing (code smell):
        df["a"][0]  # Can cause performance issues

    Preferred alternative:
        df.loc[0, "a"]  # More explicit and efficient
    """

    def __init__(self):
        super().__init__(
            name="Chain_Indexing",
            description="Using chain indexing may cause performance issues.",
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        smells = []

        # Check for Pandas library
        if not any("pandas" in lib for lib in extracted_data["libraries"]):
            return smells

        variables = extracted_data["variables"]
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Subscript) and isinstance(
                node.value, ast.Subscript
            ):
                if hasattr(node.value, "id") and node.value.id in variables:
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info="Chained indexing detected.",
                        )
                    )
        return smells
