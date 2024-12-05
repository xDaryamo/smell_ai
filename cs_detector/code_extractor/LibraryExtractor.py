import ast

class LibraryExtractor:
    def __init__(self) -> None:
        self.libraries = set()

    def extract_libraries(self, tree: any) -> set[str]:
        """
        Extracts a list of libraries used in the parsed AST tree and updates the class state.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        self.libraries.add(alias.name + ' as ' + alias.asname)
                    else:
                        self.libraries.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module != "*":
                    for alias in node.names:
                        if alias.asname:
                            self.libraries.add(node.module + '.' + alias.name + ' as ' + alias.asname)
                        else:
                            self.libraries.add(node.module + '.' + alias.name)
        return self.libraries

    def extract_library_name(self, library: str) -> str:
        return library.split(" as ")[0] if " as " in library else library

    def extract_library_as_name(self, library: str) -> str:
        return library.split(" as ")[1] if " as " in library else library

    def get_library_of_node(self, node: any) -> str:
        """
        Determines the library a node belongs to using the current list of libraries.
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
