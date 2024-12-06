import ast


class LibraryExtractor:
    def __init__(self):
        """
        Initializes the LibraryExtractor.

        Instance Variables:
        - self.libraries (set[str]): A set of libraries used in the code, extracted from the AST tree.
        """
        self.libraries = set()

    def extract_libraries(self, tree: ast.AST) -> set[str]:
        """
        Extracts all libraries used in the parsed AST tree and updates the `self.libraries` set.

        Parameters:
        - tree (ast.AST): The parsed abstract syntax tree (AST) of the code to analyze.

        Returns:
        - set[str]: A set of library names (and aliases, if any) used in the code.

        Notes:
        - Handles both `import` and `from ... import` statements.
        - Libraries are stored as strings. If an alias is present, the format is `library_name as alias`.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        self.libraries.add(alias.name + " as " + alias.asname)
                    else:
                        self.libraries.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module != "*":
                    for alias in node.names:
                        if alias.asname:
                            self.libraries.add(
                                node.module + "." + alias.name + " as " + alias.asname
                            )
                        else:
                            self.libraries.add(node.module + "." + alias.name)
        return self.libraries

    def extract_library_name(self, library: str) -> str:
        """
        Extracts the original library name from an import statement.

        Parameters:
        - library (str): The library import string (e.g., "pandas as pd" or "pandas").

        Returns:
        - str: The original library name (e.g., "pandas").

        Notes:
        - If the library string includes an alias (e.g., `as pd`), only the base library name is returned.
        """
        return library.split(" as ")[0] if " as " in library else library

    def extract_library_as_name(self, library: str) -> str:
        """
        Extracts the alias of a library from an import statement, if one exists.

        Parameters:
        - library (str): The library import string (e.g., "pandas as pd" or "pandas").

        Returns:
        - str: The alias of the library (e.g., "pd") if present. If no alias exists, returns the original library name.

        Notes:
        - If the library does not use an alias, the original library name is returned.
        """
        return library.split(" as ")[1] if " as " in library else library

    def get_library_of_node(self, node: ast.AST) -> str:
        """
        Determines the library associated with a given AST node.

        Parameters:
        - node (ast.AST): The AST node to analyze. Typically represents a function or method call.

        Returns:
        - str: The library associated with the node, or "Unknown" if the library cannot be determined.

        Notes:
        - This method inspects function calls (`ast.Call`) to see if they belong to a library in `self.libraries`.
        - For method calls (e.g., `pd.read_csv`), the method checks the base object (`pd`) to match it with a library.
        - Returns "Unknown" if the node appears to be a method of an object but the library cannot be determined.
        """
        from_object = False
        n = node
        if isinstance(n, ast.Call):
            n = n.func
            while isinstance(n, ast.Attribute):
                from_object = True
                n = n.value
            method_name = n.id if isinstance(n, ast.Name) else ""
            for lib in self.libraries:
                if method_name in lib:
                    return lib
        return "Unknown" if from_object else None
