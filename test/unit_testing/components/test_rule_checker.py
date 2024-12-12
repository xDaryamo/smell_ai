import ast
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from detection_rules.api_specific import (
    dataframe_conversion_api_misused,
    chain_indexing_smell,
)
from components.inspector import RuleChecker


class TestRuleChecker(unittest.TestCase):

    @patch("detection_rules.api_specific.chain_indexing_smell.ChainIndexingSmell")
    @patch(
        "detection_rules.api_specific.dataframe_conversion_api_misused.DataFrameConversionAPIMisused"
    )
    def test_rule_check(self, mock_dataframe_conversion, mock_chain_indexing):
        # Mock the detection methods for the smells you want to test
        mock_dataframe_conversion.return_value.detect.return_value = [
            {
                "name": "smell1",
                "line": 10,
                "description": "Description of smell1",
                "additional_info": "info1",
            },
            {
                "name": "smell2",
                "line": 15,
                "description": "Description of smell2",
                "additional_info": "info2",
            },
        ]

        mock_chain_indexing.return_value.detect.return_value = (
            []
        )  # No smell for chain indexing

        # Initialize RuleChecker
        rule_checker = RuleChecker(output_path="mock_output_path")

        # Mock the input AST node and extracted data
        mock_ast_node = MagicMock(spec=ast.AST)

        # Mocking the extracted_data to include "libraries"
        extracted_data = {"libraries": {"pandas": "pd"}, "other_data": "some_value"}

        filename = "mock_file.py"
        function_name = "my_function"

        # Initialize an empty DataFrame for storing smells
        df_output = pd.DataFrame(
            columns=[
                "filename",
                "function_name",
                "smell_name",
                "line",
                "description",
                "additional_info",
            ]
        )

        # Run the rule check method
        df_output = rule_checker.rule_check(
            ast_node=mock_ast_node,
            extracted_data=extracted_data,
            filename=filename,
            function_name=function_name,
            df_output=df_output,
        )

        # Assertions: Verify that only the expected number of smells were added (2)
        self.assertEqual(len(df_output), 2)  # Two smells were detected

        # Check the content of the smells added
        self.assertEqual(df_output.loc[0, "smell_name"], "smell1")
        self.assertEqual(df_output.loc[0, "line"], 10)
        self.assertEqual(df_output.loc[0, "description"], "Description of smell1")
        self.assertEqual(df_output.loc[0, "additional_info"], "info1")

        self.assertEqual(df_output.loc[1, "smell_name"], "smell2")
        self.assertEqual(df_output.loc[1, "line"], 15)
        self.assertEqual(df_output.loc[1, "description"], "Description of smell2")
        self.assertEqual(df_output.loc[1, "additional_info"], "info2")

    def test_no_smells(self):
        # Test the case where no smells are detected
        with patch(
            "detection_rules.api_specific.chain_indexing_smell.ChainIndexingSmell"
        ) as mock_chain_smell:
            mock_chain_smell.return_value.detect.return_value = []

            # Initialize RuleChecker
            rule_checker = RuleChecker(output_path="mock_output_path")
            mock_ast_node = MagicMock(spec=ast.AST)

            # Mocking the extracted_data to include "libraries"
            extracted_data = {"libraries": {"pandas": "pd"}, "other_data": "some_value"}

            filename = "mock_file.py"
            function_name = "my_function"

            # Initialize an empty DataFrame
            df_output = pd.DataFrame(
                columns=[
                    "filename",
                    "function_name",
                    "smell_name",
                    "line",
                    "description",
                    "additional_info",
                ]
            )

            # Run the rule check method
            df_output = rule_checker.rule_check(
                ast_node=mock_ast_node,
                extracted_data=extracted_data,
                filename=filename,
                function_name=function_name,
                df_output=df_output,
            )

            # Assertions: Verify no smells were added
            self.assertEqual(len(df_output), 0)


if __name__ == "__main__":
    unittest.main()
