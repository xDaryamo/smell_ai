import os
import pandas as pd
import ast
from detection_rules import smell
from detection_rules.api_specific import (
    chain_indexing_smell,
    dataframe_conversion_api_misused,
    gradients_not_cleared_before_backward_propagation,
    matrix_multiplication_api_misused,
    pytorch_call_method_misused,
    tensor_array_not_used,
)
from detection_rules.generic import (
    broadcasting_feature_not_used,
    columns_and_datatype_not_explicitly_set,
    deterministic_algorithm_option_not_used,
    empty_column_misinitialization,
    hyperparameters_not_explicitly_set,
    in_place_apis_misused,
    memory_not_freed,
    merge_api_parameter_not_explicitly_set,
    nan_equivalence_comparison_misused,
    unnecessary_iteration,
)


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
            chain_indexing_smell.ChainIndexingSmell(),
            dataframe_conversion_api_misused.DataFrameConversionAPIMisused(),
            gradients_not_cleared_before_backward_propagation.GradientsNotClearedSmell(),
            matrix_multiplication_api_misused.MatrixMultiplicationAPIMisused(),
            pytorch_call_method_misused.PyTorchCallMethodMisusedSmell(),
            tensor_array_not_used.TensorArrayNotUsedSmell(),
            # # Generic Smells
            # broadcasting_feature_not_used.BroadcastingFeatureNotUsedSmell(),
            # columns_and_datatype_not_explicitly_set.ColumnsAndDatatypeNotExplicitlySetSmell(),
            # deterministic_algorithm_option_not_used.DeterministicAlgorithmOptionSmell(),
            # empty_column_misinitialization.EmptyColumnMisinitializationSmell(),
            # hyperparameters_not_explicitly_set.HyperparametersNotExplicitlySetSmell(),
            # in_place_apis_misused.InPlaceAPIsMisusedSmell(),
            # memory_not_freed.MemoryNotFreedSmell(),
            # merge_api_parameter_not_explicitly_set.MergeAPIParameterNotExplicitlySetSmell(),
            # nan_equivalence_comparison_misused.NanEquivalenceComparisonMisusedSmell(),
            # unnecessary_iteration.UnnecessaryIterationSmell(),
        ]

    def rule_check(
        self,
        ast_node: ast.AST,
        extracted_data: dict[str, any],
        filename: str,
        df_output: pd.DataFrame,
    ) -> pd.DataFrame:
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

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

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
