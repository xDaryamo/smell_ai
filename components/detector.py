import os
import pandas as pd

from cs_detector.code_extractor.libraries import extract_libraries
from cs_detector.detection_rules.Generic import *
from cs_detector.detection_rules.APISpecific import *
from cs_detector.code_extractor.models import load_model_dict
from cs_detector.code_extractor.dataframe_detector import load_dataframe_dict
def rule_check(node, libraries, filename, df_output,models):
    #create dictionaries and libraries useful for detection
    df_dict = load_dataframe_dict('../obj_dictionaries/dataframes.csv')
    #start detection
    deterministic = deterministic_algorithm_option_not_used(libraries, filename, node)
    merge = merge_api_parameter_not_explicitly_set(libraries, filename, node,df_dict)
    columns_and_data = columns_and_datatype_not_explicitly_set(libraries, filename, node)
    empty = empty_column_misinitialization(libraries, filename, node,df_dict)
    nan_equivalence = nan_equivalence_comparison_misused(libraries, filename, node)
    inplace = in_place_apis_misused(libraries, filename, node)
    memory_not = memory_not_freed(libraries, filename, node, models)
    chain = Chain_Indexing(libraries, filename, node)
    dataframe_conversion = dataframe_conversion_api_misused(libraries, filename, node)
    matrix_mul = matrix_multiplication_api_misused(libraries, filename, node)
    gradients = gradients_not_cleared_before_backward_propagation(libraries, filename, node)
    tensor = tensor_array_not_used(libraries, filename, node)
    pytorch = pytorch_call_method_misused(libraries, filename, node)
 #   hyper_parameters = hyperparameters_not_explicitly_set(libraries, filename, node,models)

    if deterministic:
        df_output.loc[len(df_output)] = deterministic
    if merge:
        df_output.loc[len(df_output)] = merge
    if columns_and_data:
        df_output.loc[len(df_output)] = columns_and_data
    if empty:
        df_output.loc[len(df_output)] = empty
    if nan_equivalence:
        df_output.loc[len(df_output)] = nan_equivalence
    if inplace:
        df_output.loc[len(df_output)] = inplace
    if memory_not:
        df_output.loc[len(df_output)] = memory_not
    if chain:
        df_output.loc[len(df_output)] = chain
    if dataframe_conversion:
        df_output.loc[len(df_output)] = dataframe_conversion
    if matrix_mul:
        df_output.loc[len(df_output)] = matrix_mul
    if gradients:
        df_output.loc[len(df_output)] = gradients
    if tensor:
        df_output.loc[len(df_output)] = tensor
    if pytorch:
        df_output.loc[len(df_output)] = pytorch
 #   if hyper_parameters:
  #      df_output.loc[len(df_output)] = hyper_parameters
    return df_output

def inspect(filename):
    col = ["filename", "function_name", "smell", "name_smell", "message"]
    to_save = pd.DataFrame(columns=col)
    file_path = os.path.join(filename)
    with open(file_path, "rb") as file:
        source = file.read()
        try:
            tree = ast.parse(source)
            libraries = extract_libraries(tree)
            models = load_model_dict()
            # Visita i nodi dell'albero dell'AST alla ricerca di funzioni
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    rule_check(node, libraries, filename, to_save,models)
        except SyntaxError as e:
            message = f"Error in file {filename}: {e}"
            raise SyntaxError(message)
    return to_save
