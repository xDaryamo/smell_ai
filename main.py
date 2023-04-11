import os
import ast

from libraries import extract_libraries
from APISpecific import *
from Generic import *
import pandas as pd
from get_list_file_py import find_python_files, get_python_files


def analyze_project(project_path):
    col = ["filename", "function_name", "smell", "name_smell", "message"]
    to_save = pd.DataFrame(columns=col)
    project_name = ""
    filenames =get_python_files(project_path)

    for filename in filenames:
        file_path = os.path.join(filename)
        with open(file_path, "rb") as file:
                source = file.read()
                tree = ast.parse(source)
                libraries = extract_libraries(tree)
                # Visita i nodi dell'albero dell'AST alla ricerca di funzioni
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        print(filename)
                        deterministic = deterministic_algorithm_option_not_used(libraries, filename, node)
                        merge = merge_api_parameter_not_explicitly_set(libraries, filename, node)
                        columns_and_data = columns_and_datatype_not_explicitly_set(libraries, filename, node)
                        empty = empty_column_misinitialization(libraries, filename, node)
                        nan_equivalence = nan_equivalence_comparison_misused(libraries, filename, node)
                        inplace = in_place_apis_misused(libraries, filename, node)
                        memory_not = memory_not_freed(libraries, filename, node)
                        chain = Chain_Indexing(libraries, filename, node)
                        dataframe_conversion = dataframe_conversion_api_misused(libraries, filename, node)
                        matrix_mul = matrix_multiplication_api_misused(libraries, filename, node)
                        gradients = gradients_not_cleared_before_backward_propagation(libraries, filename, node)
                        tensor = tensor_array_not_used(libraries, filename, node)
                        pytorch = pytorch_call_method_misused(libraries, filename, node)

                        if deterministic:
                            to_save.loc[len(to_save)] = deterministic
                        if merge:
                            to_save.loc[len(to_save)] = merge
                        if columns_and_data:
                            to_save.loc[len(to_save)] = columns_and_data
                        if empty:
                            to_save.loc[len(to_save)] = empty
                        if nan_equivalence:
                            to_save.loc[len(to_save)] = nan_equivalence
                        if inplace:
                            to_save.loc[len(to_save)] = inplace
                        if memory_not:
                            to_save.loc[len(to_save)] = memory_not
                        if chain:
                            to_save.loc[len(to_save)] = chain
                        if dataframe_conversion:
                            to_save.loc[len(to_save)] = dataframe_conversion
                        if matrix_mul:
                            to_save.loc[len(to_save)] = matrix_mul
                        if gradients:
                            to_save.loc[len(to_save)] = gradients
                        if tensor:
                            to_save.loc[len(to_save)] = tensor
                        if pytorch:
                            to_save.loc[len(to_save)] = pytorch

       # for dirname in dirnames:
       #     new_path = os.path.join(dirpath, dirname)
       #     analyze_project(new_path)
    to_save.to_csv("output/to_save.csv", index=False, mode='a')


analyze_project("/Users/broke31/Desktop/smell_ai")
