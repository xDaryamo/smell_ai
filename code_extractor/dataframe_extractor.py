import ast
import pandas as pd

class DataFrameExtractor:
    def __init__(self, df_dict_path: str):
        """
        Initializes the DataFrameExtractor.

        Parameters:
        - df_dict_path (str): Path to the CSV file containing the DataFrame method definitions.

        Instance Variables:
        - self.libraries (set[str]): A set of library imports provided during initialization.
        - self.df_dict (dict[str, list]): A dictionary representing DataFrame-related methods (loaded from CSV).
        - self.df_dict_path (str): Path to the DataFrame method definitions file.
        """
        self.libraries = None
        self.df_dict = None
        self.df_dict_path = df_dict_path

    def set_libraries(libraries: set[str]) -> None:
         """
        Initializes the DataFrameExtractor libraries instance variable

        Parameters:
        - libraries (set[str]): A set of libraries used in the code (e.g., {"pandas as pd"}).
         """
        self.libraries = libraries

    def load_dataframe_dict(self) -> dict[str, list]:
        """
        Loads the DataFrame methods dictionary from a CSV file.

        Returns:
        - dict[str, list]: A dictionary where the keys are column names from the CSV, and the values are lists of column data.

        Raises:
        - FileNotFoundError: If the CSV file cannot be found.
        """
        self.df_dict = pd.read_csv(self.df_dict_path, dtype={'id': 'string', 'library': 'string', 'method': 'string'}).to_dict(orient='list')
        return self.df_dict

    def search_pandas_library(self) -> str:
        """
        Searches for the pandas library in the stored library list.

        Returns:
        - str: The alias of the pandas library (e.g., "pd") if found, or None if pandas is not used.

        Notes:
        - This method assumes that the library is imported with an alias (e.g., `import pandas as pd`).
        - If pandas is imported without an alias, this method will return None.
        """
        for lib in self.libraries:
            short = self.extract_lib_object(lib)
            if short:
                return short
        return None

    def dataframe_check(self, fun_node: ast.AST) -> list[str]:
        """
        Checks if a function node uses pandas DataFrames.

        Parameters:
        - fun_node (ast.AST): The AST node representing the function to analyze.

        Returns:
        - list[str]: A list of variables related to pandas DataFrames, or None if pandas is not used.

        Notes:
        - Uses `search_pandas_library` to ensure pandas is being used.
        - Initiates a recursive search for variables starting from the pandas alias.
        """
        short = self.search_pandas_library()
        if short is None:
            return None
        return self.recursive_search_variables(fun_node, [short])

    def recursive_search_variables(self, fun_node: ast.AST, init_list: list[str]) -> list[str]:
        """
        Recursively searches for variables within a function node related to DataFrame operations.

        Parameters:
        - fun_node (ast.AST): The AST node representing the function to analyze.
        - init_list (list[str]): A list of initial variable names to start the search.

        Returns:
        - list[str]: A list of variables related to pandas DataFrame operations.

        Notes:
        - The method analyzes assignments to identify variables that interact with DataFrame-related variables.
        - Recursion continues until no new variables are added to the list.
        """
        list_vars = init_list.copy()
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Assign):
                # Case 1: Right-hand side is an expression involving a variable in list_vars
                if isinstance(node.value, ast.Expr):
                    expr = node.value
                    if isinstance(expr.value, ast.Name) and expr.value.id in list_vars:
                        if hasattr(node.targets[0], 'id') and node.targets[0].id not in list_vars:
                            list_vars.append(node.targets[0].id)

                # Case 2: Right-hand side is a variable name already in list_vars
                if isinstance(node.value, ast.Name) and node.value.id in list_vars:
                    if hasattr(node.targets[0], 'id') and node.targets[0].id not in list_vars:
                        list_vars.append(node.targets[0].id)

                # Case 3: Right-hand side is a function call using a variable in list_vars
                if isinstance(node.value, ast.Call):
                    name_func = node.value.func
                    if isinstance(name_func, ast.Attribute):
                        id = None
                        if isinstance(name_func.value, ast.Subscript) and isinstance(name_func.value.value, ast.Name):
                            id = name_func.value.value.id
                        elif isinstance(name_func.value, ast.Name):
                            id = name_func.value.id
                        if id in list_vars and name_func.attr in self.df_dict['method']:
                            if hasattr(node.targets[0], 'id') and node.targets[0].id not in list_vars:
                                list_vars.append(node.targets[0].id)

                # Case 4: Right-hand side is a subscript involving a variable in list_vars
                elif isinstance(node.value, ast.Subscript) and isinstance(node.value.value, ast.Name):
                    if node.value.value.id in list_vars:
                        if hasattr(node.targets[0], 'id') and node.targets[0].id not in list_vars:
                            list_vars.append(node.targets[0].id)

        # Recursive call if new variables were added, otherwise return the final list
        if list_vars == init_list:
            return list_vars
        else:
            return self.recursive_search_variables(fun_node, list_vars)

    def extract_lib_object(self, lib: str) -> str:
        """
        Extracts the alias of a library from an import statement.

        Parameters:
        - lib (str): The library import string (e.g., "pandas as pd").

        Returns:
        - str: The alias of the library (e.g., "pd") if present, or None otherwise.

        Notes:
        - If the library string does not include an alias, this method will return None.
        """
        split_lib = lib.split(" as ")
        return split_lib[1] if len(split_lib) > 1 else None

    def get_dataframe_variables(self, variables: list[str]) -> list[str]:
        """
        Identifies DataFrame-related variables.

        Parameters:
        - variables (list[str]): A list of variable names.

        Returns:
        - list[str]: Variables associated with DataFrame operations.
        """
        dataframe_vars = []
        for var in variables:
            if self.df_dict and 'method' in self.df_dict:
                if var in self.df_dict['method']:
                    dataframe_vars.append(var)
        return dataframe_vars