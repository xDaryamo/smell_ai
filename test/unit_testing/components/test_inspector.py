import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import ast
from components.inspector import Inspector


class TestInspector(unittest.TestCase):

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("ast.parse")
    @patch("components.inspector.LibraryExtractor")
    @patch("components.inspector.VariableExtractor")
    @patch("components.inspector.DataFrameExtractor")
    @patch("components.inspector.ModelExtractor")
    @patch("components.inspector.RuleChecker")
    def test_inspect(
        self,
        MockRuleChecker,
        MockModelExtractor,
        MockDataFrameExtractor,
        MockVariableExtractor,
        MockLibraryExtractor,
        mock_ast_parse,
        mock_open,
    ):
        # Setup mocks for extractors and rule checker
        mock_rule_checker = MagicMock()
        mock_model_extractor = MagicMock()
        mock_data_frame_extractor = MagicMock()
        mock_variable_extractor = MagicMock()
        mock_library_extractor = MagicMock()

        # Setup mock return values for the extractors
        mock_library_extractor.get_library_aliases.return_value = {
            "pandas": "pd"
        }
        mock_variable_extractor.extract_variable_definitions.return_value = [
            "var1",
            "var2",
        ]
        mock_data_frame_extractor.extract_dataframe_variables.return_value = [
            "df_var1",
            "df_var2",
        ]
        mock_model_extractor.model_dict = {"model1": "details"}
        mock_model_extractor.tensor_operations_dict = {
            "operation": ["tensor_op1", "tensor_op2"]
        }
        mock_model_extractor.load_model_methods.return_value = {
            "method1": "details"
        }

        # Mock the rule_check to return a real DataFrame
        mock_rule_checker.rule_check.return_value = pd.DataFrame(
            data=[
                [
                    "mock_file.py",
                    "my_function",
                    "smell1",
                    10,
                    "description1",
                    "info1",
                ],
                [
                    "mock_file.py",
                    "my_function",
                    "smell2",
                    15,
                    "description2",
                    "info2",
                ],
            ],
            columns=[
                "filename",
                "function_name",
                "smell_name",
                "line",
                "description",
                "additional_info",
            ],
        )

        # Mock the content of the file being read
        mock_file_contents = """\
import pandas as pd

def my_function():
    df = pd.DataFrame()
    return df
"""
        mock_open.return_value.read.return_value = mock_file_contents

        # Mock AST parsing to return a tree with function definitions
        mock_ast_parse.return_value = ast.Module(
            body=[
                ast.FunctionDef(
                    name="my_function",
                    args=ast.arguments(
                        args=[],
                        vararg=None,
                        kwonlyargs=[],
                        kw_defaults=[],
                        kwarg=None,
                    ),
                    body=[
                        ast.Assign(
                            targets=[ast.Name(id="df", ctx=ast.Store())],
                            value=ast.Call(
                                func=ast.Name(
                                    id="pd.DataFrame", ctx=ast.Load()
                                ),
                                args=[],
                                keywords=[],
                            ),
                        )
                    ],
                    decorator_list=[],
                    lineno=1,
                )
            ]
        )

        # Instantiate Inspector
        inspector = Inspector(output_path="mock_output_path")
        inspector.rule_checker = mock_rule_checker

        # Call the inspect method
        result = inspector.inspect("mock_file.py")

        # Assertions
        # Ensure open was called with the correct file path
        mock_open.assert_called_once_with(
            os.path.abspath("mock_file.py"), "r", encoding="utf-8"
        )

        # Ensure AST parse was called correctly
        mock_ast_parse.assert_called_once()

        # Ensure that rule_check was called once
        mock_rule_checker.rule_check.assert_called_once()

        # Ensure the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        # Ensure that the DataFrame has the correct columns
        expected_columns = [
            "filename",
            "function_name",
            "smell_name",
            "line",
            "description",
            "additional_info",
        ]
        self.assertListEqual(list(result.columns), expected_columns)

        # Ensure the DataFrame is not empty
        # (for example, checking if rule_check was called)
        self.assertGreater(len(result), 0)
