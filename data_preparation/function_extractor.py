import ast


class FunctionExtractor:
    """
    A class to analyze Python files and extract functions using AST.
    """

    def __init__(self, file_path):
        """
        Initializes the FunctionExtractor with a specific file path.
        Args:
            file_path (str): Path to the Python file to analyze.
        """
        self.file_path = file_path
        self.imported_libraries = []
        self.functions = []

    def parse_file(self):
        """
        Parses the file content and populates imported libraries and functions.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Parse file content using AST
            tree = ast.parse(file_content)

            # Process each node in the file
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imported_libraries.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    self.imported_libraries.append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    function_name = node.name
                    function_code = ast.unparse(
                        node
                    )  # Converts AST node to Python code
                    self.functions.append(
                        {
                            "file_path": self.file_path,
                            "function_name": function_name,
                            "libraries_used": list(
                                set(self.imported_libraries)
                            ),
                            "code": function_code,
                        }
                    )
        except Exception as e:
            print(f"Error processing file {self.file_path}: {e}")

    def get_functions(self):
        """
        Returns the list of extracted functions.
        """
        return self.functions
