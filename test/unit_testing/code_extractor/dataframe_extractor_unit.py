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


if __name__ == "__main__":
    unittest.main()
