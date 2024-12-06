import ast
from detection_rules.smell import Smell


class BroadcastingFeatureNotUsedSmell(Smell):
    """
    Detects cases where TensorFlow's broadcasting feature is not used, and tiling is applied unnecessarily.

    Example of code smell:
        tensor_a = tf.constant([[1], [2], [3]])
        tensor_b = tf.constant([1, 2, 3])
        tensor_c = tf.tile(tensor_a, [1, 3]) + tensor_b  # Inefficient tiling

    Preferred alternative:
        Use broadcasting:
        tensor_a = tf.constant([[1], [2], [3]])
        tensor_b = tf.constant([1, 2, 3])
        tensor_c = tensor_a + tensor_b  # Broadcasting applied
    """

    def __init__(self):
        super().__init__(
            name="broadcasting_feature_not_used",
            description=(
                "Using broadcasting in TensorFlow is preferred over tiling arrays unnecessarily. "
                "Broadcasting allows arithmetic between arrays of different shapes, saving memory and computation time."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        smells = []

        # Check for Tensorflow library
        library_alias = extracted_data["library_aliases"].get("tensorflow", None)
        if not library_alias:
            return smells

        tensor_variables = {}
        tensor_dict = extracted_data.get("tensor_operations", [])

        # Traverse the AST nodes to find TensorFlow constants and variables
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Assign):
                if (
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr in {"constant", "Variable"}
                    and getattr(node.value.func.value, "id", None) == library_alias
                ):
                    if hasattr(node.targets[0], "id"):
                        tensor_name = node.targets[0].id
                        tensor_constants = self._extract_tensor_constants(node.value)
                        if tensor_constants:
                            tensor_variables[tensor_name] = tensor_constants

        # Check for tiling operations
        tensor_variables_with_tiling = self._tensor_check_tiling(
            ast_node, tensor_variables
        )

        # Find tensor operations and check for broadcasting opportunities
        operations = self._search_tensor_combination_operation(
            ast_node, tensor_dict, tensor_variables
        )
        broadcasting_checking_tensors = self._check_broadcasting(
            operations, tensor_variables, tensor_variables_with_tiling
        )

        # Add detected smells
        for tensor in broadcasting_checking_tensors:
            smells.append(
                self.format_smell(
                    line=tensor["line"],
                    additional_info=(
                        "Broadcasting allows arrays of different shapes to be used in arithmetic operations, "
                        "avoiding unnecessary tiling."
                    ),
                )
            )

        return smells

    def _extract_tensor_constants(self, node: ast.Call) -> list:
        """
        Extracts constants from a TensorFlow tensor creation call.

        :param node: The AST node representing a tensor creation call.
        :return: A list of constants if found, otherwise an empty list.
        """
        if not hasattr(node, "args") or len(node.args) == 0:
            return []
        arg = node.args[0]
        if isinstance(arg, ast.List):
            return [elt for elt in arg.elts if isinstance(elt, ast.Constant)]
        return []

    def _tensor_check_tiling(
        self, fun_node: ast.AST, tensor_variables: dict
    ) -> list[str]:
        """
        Identifies tensor variables that have undergone tiling operations.

        :param fun_node: The AST node representing the function.
        :param tensor_variables: Dictionary of tensor variables and their properties.
        :return: List of tensor variables with tiling applied.
        """
        # Implement tiling detection logic (placeholder)
        return []

    def _search_tensor_combination_operation(
        self, fun_node: ast.AST, tensor_dict: list[str], tensor_variables: dict
    ) -> list[ast.Call]:
        """
        Searches for operations involving tensor combinations.

        :param fun_node: The AST node representing the function.
        :param tensor_dict: List of tensor operation methods.
        :param tensor_variables: Dictionary of tensor variables.
        :return: List of AST nodes representing combination operations.
        """
        # Implement tensor combination detection logic (placeholder)
        return []

    def _check_broadcasting(
        self,
        operations: list[ast.Call],
        tensor_variables: dict,
        tensor_variables_with_tiling: list[str],
    ) -> list[dict[str, any]]:
        """
        Checks whether tensor operations can benefit from broadcasting instead of tiling.

        :param operations: List of AST nodes representing operations.
        :param tensor_variables: Dictionary of tensor variables.
        :param tensor_variables_with_tiling: List of tensor variables with tiling applied.
        :return: List of tensors where broadcasting could be applied.
        """
        # Implement broadcasting check logic (placeholder)
        return []
