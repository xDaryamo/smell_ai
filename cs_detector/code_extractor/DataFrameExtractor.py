import ast
import pandas as pd

class DataFrameExtractor:
    
    def __init__(self, libraries: set[str], df_dict_path: str) -> None:
        self.libraries = libraries
        self.df_dict = None
        self.df_dict_path = df_dict_path

    def load_dataframe_dict(self) -> dict[str, str, str]:
        """
        Loads the DataFrame methods dictionary from a CSV file.
        """
        self.df_dict = pd.read_csv(self.df_dict_path, dtype={'id': 'string', 'library': 'string', 'method': 'string'})
        return self.df_dict

    def search_pandas_library(self) -> str:
        """
        Searches for pandas in the stored library list.
        """
        for lib in self.libraries:
            short = self.extract_lib_object(lib)
            if short:
                return short
        return None

    def dataframe_check(self, fun_node: any) -> List[str]:
        """
        Checks if a function node uses pandas DataFrames.
        """
        short = self.search_pandas_library()
        if short is None:
            return None
        return self.recursive_search_variables(fun_node, [short])

    def recursive_search_variables(self, fun_node: any, init_list: list[str]) -> list[str]:
        list_vars = init_list.copy()
        for node in ast.walk(fun_node):
            # Check assignments
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
                        if id in list_vars and name_func.attr in self.df_dict['method'].tolist():
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
        Extracts the alias for a library.
        """
        split_lib = lib.split(" as ")
        return split_lib[1] if len(split_lib) > 1 else None

    def extract_variables(self, list_variables):
        """
        Placeholder for extracting additional variables (to be implemented).
        """
        pass