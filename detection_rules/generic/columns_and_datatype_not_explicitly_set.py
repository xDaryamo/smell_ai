import ast
from detection_rules.smell import Smell


class ColumnsAndDatatypeNotExplicitlySetSmell(Smell):
    """
    Detects cases where Pandas' DataFrame or read_csv methods are used without explicitly specifying column names or datatypes.

    Example of code smell:
        pd.DataFrame(data)  # Missing explicit 'dtype'
        pd.read_csv("file.csv")  # Missing explicit 'dtype'

    Preferred alternative:
        pd.DataFrame(data, dtype="float")  # Specify dtype
        pd.read_csv("file.csv", dtype={"column1": "int", "column2": "float"})
    """

    def __init__(self):
        super().__init__(
            name="columns_and_datatype_not_explicitly_set",
            description=(
                "Pandas' DataFrame or read_csv methods should explicitly set 'dtype' to avoid unexpected behavior."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:

        smells = []

        # Check for Pandas library
        if not any("pandas" in lib for lib in extracted_data["libraries"]):
            return smells

        library_name = extracted_data["library_aliases"].get("pandas", None)

        if not library_name:
            return smells

        # Traverse the AST nodes
        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Call)
                and hasattr(node.func, "attr")
                and node.func.attr in {"DataFrame", "read_csv"}
                and hasattr(node.func.value, "id")
                and node.func.value.id == library_name
            ):
                # Check for missing or incomplete keyword arguments
                if not hasattr(node, "keywords") or not node.keywords:
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info="Missing explicit 'dtype' in DataFrame or read_csv call.",
                        )
                    )
        return smells
