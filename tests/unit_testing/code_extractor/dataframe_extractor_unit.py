import unittest
import ast
import pandas as pd
from io import StringIO
from code_extractor.dataframe_extractor import DataFrameExtractor


class TestDataFrameExtractor(unittest.TestCase):

    def setUp(self):
        """Set up test cases with a sample DataFrame method list and example code."""
        self.method_csv = StringIO("method\nhead\nmerge\n")
        self.extractor = DataFrameExtractor()
        self.extractor.load_dataframe_dict(self.method_csv)

        # Sample code snippets for different scenarios
        self.sample_code = """
        import pandas as pd

        def test_function(df, other_df):
            df = pd.DataFrame({'a': [1, 2, 3]})
            other_df = df.head()
            result = other_df.merge(df, on='a')
            print(df['a'])
        """

        self.empty_function_code = "def empty_function(): pass"
        self.nested_calls_code = """
        import pandas as pd
        def nested_function():
            df = pd.DataFrame({'a': [1, 2, 3]}).head()
            result = df.merge(df, on='a')
            print(df['a'])
        """
        self.no_pandas_alias_code = """
        import pandas
        def no_alias_function():
            df = pandas.DataFrame({'a': [1, 2, 3]})
        """
        self.complex_subscript_access_code = """
        import pandas as pd
        def complex_access_function():
            df = pd.DataFrame({'a': [1, 2, 3]})
            col = 'a'
            print(df[col])
        """

    def parse_function(self, code):
        """Helper method to parse code and extract the function node."""
        tree = ast.parse(code)
        return next(
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        )

    def test_load_dataframe_dict(self):
        """Test loading of DataFrame methods from a CSV."""
        self.assertEqual(self.extractor.df_methods, ["head", "merge"])

    def test_extract_dataframe_variables(self):
        """Test extraction of DataFrame variables."""
        function_node = self.parse_function(self.sample_code)
        dataframe_vars = self.extractor.extract_dataframe_variables(
            function_node, alias="pd"
        )
        self.assertListEqual(sorted(dataframe_vars), ["df", "other_df", "result"])

    def test_track_dataframe_methods(self):
        """Test tracking of DataFrame methods."""
        function_node = self.parse_function(self.sample_code)
        dataframe_vars = self.extractor.extract_dataframe_variables(
            function_node, alias="pd"
        )
        method_usage = self.extractor.track_dataframe_methods(
            function_node, dataframe_vars
        )
        self.assertDictEqual(
            method_usage,
            {
                "df": ["head"],
                "other_df": ["merge"],
                "result": [],
            },
        )

    def test_track_dataframe_accesses(self):
        """Test tracking of DataFrame column accesses."""
        function_node = self.parse_function(self.sample_code)
        dataframe_vars = self.extractor.extract_dataframe_variables(
            function_node, alias="pd"
        )
        accesses = self.extractor.track_dataframe_accesses(
            function_node, dataframe_vars
        )
        self.assertDictEqual(accesses, {"df": ["a"], "other_df": [], "result": []})

    def test_empty_function(self):
        """Test with an empty function node."""
        function_node = self.parse_function(self.empty_function_code)
        dataframe_vars = self.extractor.extract_dataframe_variables(
            function_node, alias="pd"
        )
        self.assertListEqual(dataframe_vars, [])

        method_usage = self.extractor.track_dataframe_methods(
            function_node, dataframe_vars
        )
        self.assertDictEqual(method_usage, {})

        accesses = self.extractor.track_dataframe_accesses(
            function_node, dataframe_vars
        )
        self.assertDictEqual(accesses, {})

    def test_nested_dataframe_calls(self):
        """Test nested DataFrame calls."""
        function_node = self.parse_function(self.nested_calls_code)
        dataframe_vars = self.extractor.extract_dataframe_variables(
            function_node, alias="pd"
        )
        self.assertListEqual(sorted(dataframe_vars), ["df", "result"])

        method_usage = self.extractor.track_dataframe_methods(
            function_node, dataframe_vars
        )
        self.assertDictEqual(
            method_usage,
            {
                "df": ["merge"],
                "result": [],
            },
        )

        accesses = self.extractor.track_dataframe_accesses(
            function_node, dataframe_vars
        )
        self.assertDictEqual(accesses, {"df": ["a"], "result": []})

    def test_no_pandas_alias(self):
        """Test function that uses Pandas without aliasing."""
        function_node = self.parse_function(self.no_pandas_alias_code)
        dataframe_vars = self.extractor.extract_dataframe_variables(
            function_node, alias="pd"
        )
        self.assertListEqual(dataframe_vars, [])

    def test_complex_subscript_access(self):
        """Test for DataFrame accesses with non-constant keys."""
        function_node = self.parse_function(self.complex_subscript_access_code)
        dataframe_vars = self.extractor.extract_dataframe_variables(
            function_node, alias="pd"
        )
        accesses = self.extractor.track_dataframe_accesses(
            function_node, dataframe_vars
        )

        # Non-constant keys should not be tracked
        self.assertDictEqual(accesses, {"df": []})

    def test_malformed_csv(self):
        """Test loading a malformed CSV file."""
        malformed_csv = StringIO("not_method_column\nhead\nmerge\n")
        with self.assertRaises(KeyError):
            self.extractor.load_dataframe_dict(malformed_csv)

    def test_large_ast(self):
        """Test handling of a large AST."""
        large_code = "\n".join(
            [f"def function_{i}(): df = pd.DataFrame()" for i in range(1000)]
        )
        tree = ast.parse(large_code)

        for function_node in [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]:
            dataframe_vars = self.extractor.extract_dataframe_variables(
                function_node, alias="pd"
            )
            self.assertListEqual(dataframe_vars, ["df"])

    def test_aliasing_dataframe_name(self):
        """Test when DataFrame is assigned to another variable."""
        aliasing_code = """
        import pandas as pd
        def aliasing_function():
            df1 = pd.DataFrame({'a': [1, 2, 3]})
            df2 = df1
        """
        function_node = self.parse_function(aliasing_code)
        dataframe_vars = self.extractor.extract_dataframe_variables(
            function_node, alias="pd"
        )
        self.assertListEqual(sorted(dataframe_vars), ["df1", "df2"])


if __name__ == "__main__":
    unittest.main()
