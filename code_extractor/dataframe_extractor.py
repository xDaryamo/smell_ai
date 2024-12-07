import ast
import pandas as pd


class DataFrameExtractor:
    """
    A utility class for extracting information related to Pandas DataFrames
    from Python code represented as an Abstract Syntax Tree (AST).
    """

    def __init__(self, df_dict_path: str = None):
        """
        Initializes the DataFrameExtractor.

        Parameters:
        - df_dict_path (str): Optional path to the CSV file containing the DataFrame method definitions.

        Instance Variables:
        - self.df_methods (list[str]): A list of Pandas DataFrame methods loaded from the CSV file.
        """
        self.df_methods = []
        if df_dict_path:
            self.load_dataframe_dict(df_dict_path)

    def load_dataframe_dict(self, path: str):
        """
        Loads a dictionary of Pandas DataFrame methods from a CSV file.

        Parameters:
        - path (str): Path to the CSV file.

        Returns:
        - None: Updates `self.df_methods` with a list of method names.
        """
        df = pd.read_csv(path, dtype={"method": "string"})
        self.df_methods = df["method"].tolist()

    def extract_dataframe_variables(self, fun_node: ast.AST, alias: str) -> list[str]:
        """
        Identifies variables initialized as Pandas DataFrames in a function.

        Parameters:
        - fun_node (ast.AST): The AST node representing a Python function.
        - alias (str): The alias used for Pandas (e.g., "pd").

        Returns:
        - list[str]: A list of variable names initialized as DataFrames.

        Example:
        ----------
        Code:
            def example():
                df = pd.DataFrame({'a': [1, 2, 3]})
                result = df['a']

        Output:
            ['df']
        """
        dataframe_vars = []
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Assign):  # Look for assignment statements
                if isinstance(
                    node.value, ast.Call
                ):  # Check if right-hand side is a function call
                    func = node.value.func
                    if (
                        isinstance(func, ast.Attribute)
                        and isinstance(func.value, ast.Name)
                        and func.value.id == alias
                        and func.attr == "DataFrame"
                    ):
                        for target in node.targets:
                            if isinstance(
                                target, ast.Name
                            ):  # Ensure it's a simple variable
                                dataframe_vars.append(target.id)
        return dataframe_vars

    def track_dataframe_methods(
        self, fun_node: ast.AST, dataframe_vars: list[str]
    ) -> dict[str, list[str]]:
        """
        Tracks methods called on Pandas DataFrames within a function.

        Parameters:
        - fun_node (ast.AST): The AST node representing a Python function.
        - dataframe_vars (list[str]): A list of DataFrame variable names.

        Returns:
        - dict[str, list[str]]: A dictionary where keys are DataFrame variable names,
          and values are lists of method names called on those DataFrames.

        Example:
        ----------
        Code:
            def example():
                df = pd.DataFrame({'a': [1, 2, 3]})
                df2 = df.drop('a', axis=1)

        Output:
            {
                'df': ['drop'],
                'df2': []
            }
        """
        methods_usage = {var: [] for var in dataframe_vars}
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Call):  # Look for function/method calls
                func = node.func
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                    if func.value.id in dataframe_vars and func.attr in self.df_methods:
                        methods_usage[func.value.id].append(func.attr)
        return methods_usage

    def track_dataframe_accesses(
        self, fun_node: ast.AST, dataframe_vars: list[str]
    ) -> dict[str, list[str]]:
        """
        Tracks column accesses on Pandas DataFrames within a function.

        Parameters:
        - fun_node (ast.AST): The AST node representing a Python function.
        - dataframe_vars (list[str]): A list of DataFrame variable names.

        Returns:
        - dict[str, list[str]]: A dictionary where keys are DataFrame variable names,
          and values are lists of column names accessed on those DataFrames.

        Example:
        ----------
        Code:
            def example():
                df = pd.DataFrame({'a': [1, 2, 3]})
                result = df['a']

        Output:
            {
                'df': ['a']
            }
        """
        accesses = {var: [] for var in dataframe_vars}
        for node in ast.walk(fun_node):
            if isinstance(
                node, ast.Subscript
            ):  # Look for subscript accesses (e.g., df['a'])
                if isinstance(node.value, ast.Name) and node.value.id in dataframe_vars:
                    if isinstance(
                        node.slice, ast.Constant
                    ):  # Ensure the key is a constant
                        accesses[node.value.id].append(node.slice.value)
        return accesses
