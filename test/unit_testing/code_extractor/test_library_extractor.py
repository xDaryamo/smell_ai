import unittest
import ast
from code_extractor.library_extractor import LibraryExtractor


class TestLibraryExtractor(unittest.TestCase):

    def setUp(self):
        """Set up a new LibraryExtractor instance for each test."""
        self.extractor = LibraryExtractor()

    def test_extract_libraries(self):
        """Test extracting libraries from an AST."""
        code = """
import pandas as pd
from numpy import array
from matplotlib import pyplot as plt
"""
        tree = ast.parse(code)
        libraries = self.extractor.extract_libraries(tree)
        expected_libraries = [
            {"name": "pandas", "alias": "pd"},
            {"name": "numpy.array", "alias": None},
            {"name": "matplotlib.pyplot", "alias": "plt"},
        ]
        self.assertListEqual(libraries, expected_libraries)

    def test_extract_libraries_no_alias(self):
        """Test case where libraries are imported without aliases."""
        code = """
import pandas
import numpy
"""
        tree = ast.parse(code)
        libraries = self.extractor.extract_libraries(tree)
        expected_libraries = [
            {"name": "pandas", "alias": None},
            {"name": "numpy", "alias": None},
        ]
        self.assertListEqual(libraries, expected_libraries)

    def test_get_library_aliases(self):
        """Test getting library aliases."""
        libraries = [
            {"name": "pandas", "alias": "pd"},
            {"name": "numpy.array", "alias": None},
        ]
        aliases = self.extractor.get_library_aliases(libraries)
        expected_aliases = {"pandas": "pd", "numpy.array": "numpy.array"}
        self.assertDictEqual(aliases, expected_aliases)

    def test_get_library_of_node_method_call(self):
        """Test getting the library for a method call."""
        code = "import pandas as pd; pd.read_csv('file.csv')"
        tree = ast.parse(code)

        # Find the first Call node (method call like `pd.read_csv()`)
        node = None
        for item in tree.body:
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
                node = item.value
                break

        libraries = [
            {"name": "pandas", "alias": "pd"},
            {"name": "numpy.array", "alias": None},
        ]
        aliases = self.extractor.get_library_aliases(libraries)
        library_name = self.extractor.get_library_of_node(node, aliases)
        self.assertEqual(library_name, "pandas")

    def test_get_library_of_node_function_call(self):
        """Test getting the library for a function call."""
        code = "import pandas as pd; pd.DataFrame()"
        tree = ast.parse(code)

        # Find the first Call node (function call like `pd.DataFrame()`)
        node = None
        for item in tree.body:
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
                node = item.value
                break

        libraries = [
            {"name": "pandas", "alias": "pd"},
            {"name": "numpy.array", "alias": None},
        ]
        aliases = self.extractor.get_library_aliases(libraries)
        library_name = self.extractor.get_library_of_node(node, aliases)
        self.assertEqual(library_name, "pandas")

    def test_get_library_of_node_unknown(self):
        """Test getting 'Unknown' for a node that
        does not belong to any known library."""
        code = "print('hello world')"
        tree = ast.parse(code)
        node = tree.body[0].value  # Get the print function call
        libraries = [
            {"name": "pandas", "alias": "pd"},
            {"name": "numpy.array", "alias": None},
        ]
        aliases = self.extractor.get_library_aliases(libraries)
        library_name = self.extractor.get_library_of_node(node, aliases)
        self.assertEqual(library_name, "Unknown")

    def test_extract_libraries_empty_code(self):
        """Test extracting libraries from empty code."""
        code = ""
        tree = ast.parse(code)
        libraries = self.extractor.extract_libraries(tree)
        self.assertEqual(libraries, [])

    def test_get_library_aliases_empty(self):
        """Test getting aliases from an empty list."""
        libraries = []
        aliases = self.extractor.get_library_aliases(libraries)
        self.assertEqual(aliases, {})

    def test_get_library_of_node_empty(self):
        """Test getting the library of an empty AST."""
        node = None  # No node to inspect
        aliases = {}
        library_name = self.extractor.get_library_of_node(node, aliases)
        self.assertEqual(library_name, "Unknown")


if __name__ == "__main__":
    unittest.main()
