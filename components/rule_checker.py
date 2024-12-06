import os
import pandas as pd
import ast
from detection_rules import Smell
from detection_rules.api_specific import *
from detection_rules.generic import *

class RuleChecker:
    def __init__(self, output_path: str):
        """
        Initializes the RuleChecker.

        Parameters:
        - output_path (str): Path where detected smells will be saved.
        """
        self.output_path = output_path
        self.smells = None

    def setup_smells(self) -> None:
    """
    Sets up the smells for the RuleChecker by explicitly instantiating them.
    """
        self.smells = [
            # API-Specific Smells
            ChainIndexingSmell(),
            DataFrameConversionApiMisusedSmell(),
            GradientsNotClearedBeforeBackpropSmell(),
            MatrixMultiplicationApiMisusedSmell(),
            PytorchCallMethodMisusedSmell(),
            TensorArrayNotUsedSmell(),

            # Generic Smells
            BroadcastingFeatureNotUsedSmell(),
            ColumnsAndDatatypeNotExplicitlySetSmell(),
            DeterministicAlgorithmOptionNotUsedSmell(),
            EmptyColumnMisinitializationSmell(),
            HyperparametersNotExplicitlySetSmell(),
            InPlaceApisMisusedSmell(),
            MemoryNotFreedSmell(),
            MergeApiParameterNotExplicitlySetSmell(),
            NanEquivalenceComparisonMisusedSmell(),
            UnnecessaryIterationSmell(),
        ]

    def rule_check(self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str, df_output: pd.DataFrame) -> pd.Dataframe:
        """
        Applies all registered smell detectors to the given AST node.

        Parameters:
        - ast_node (ast.AST): The AST node to analyze.
        - extracted_data (dict): Pre-extracted data (e.g., libraries, variables, etc.).
        - filename (str): The name of the file being analyzed.
        - df_output (pd.DataFrame): The DataFrame to store detected smells.

        Returns:
        - pd.DataFrame: The updated DataFrame containing detected smells.
        """
        for smell in self.smells:
            detected_smells = smell.detect(ast_node, extracted_data, filename)

            for detected_smell in detected_smells:
                df_output.loc[len(df_output)] = {
                    "filename": filename,
                    "smell_name": detected_smell["name"],
                    "line": detected_smell["line"],
                    "description": detected_smell["description"],
                    "additional_info": detected_smell["additional_info"],
                }
                self.save_single_file(filename, [detected_smell])

        return df_output

    def save_single_file(self, filename: str, smell_list: list[dict[str, any]]) -> None:
        """
        Saves detected smells to a CSV file.

        Parameters:
        - filename (str): The name of the file being analyzed.
        - smell_list (list[dict[str, any]]): A list of dictionaries containing detected smells.

        Returns:
        - None
        """
        if not smell_list:
            return

        cols = ["filename", "smell_name", "line", "description", "additional_info"]
        smell_name = smell_list[0]["name"]

        output_file = os.path.join(self.output_path, f"{smell_name}.csv")

        if os.path.exists(output_file):
            to_save = pd.read_csv(output_file)
        else:
            to_save = pd.DataFrame(columns=cols)

        for smell in smell_list:
            to_save.loc[len(to_save)] = {
                "filename": filename,
                "smell_name": smell["name"],
                "line": smell["line"],
                "description": smell["description"],
                "additional_info": smell["additional_info"],
            }

        to_save.to_csv(output_file, index=False)
