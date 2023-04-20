import os
import ast

from libraries import extract_libraries
from APISpecific import *
from Generic import *
import pandas as pd
from get_list_file_py import find_python_files, get_python_files
import subprocess
import hityper
def analyze_project(project_path, output_path="."):


    col = ["filename", "function_name", "smell", "name_smell", "message"]
    to_save = pd.DataFrame(columns=col)
    filenames = get_python_files(project_path)

    for filename in filenames:
        file_path = os.path.join(filename)
        with open(file_path, "rb") as file:
            source = file.read()
            try:
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
            except Exception as e:
                message = f"Error in file {filename}: {e}"
                error_path = output_path.replace("output", "error")
                if not os.path.exists(error_path):
                    os.makedirs(error_path)
                with open(f"{error_path}/error.txt", "a") as error_file:
                    error_file.write(message)
                continue

    # for dirname in dirnames:
    #     new_path = os.path.join(dirpath, dirname)
    #     analyze_project(new_path)
    to_save.to_csv(output_path + "/to_save.csv", index=False, mode='a')


# analyze_project("/Users/broke31/Desktop/smell_ai")

def projects_analysis(BASE_PATH, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    dirpath = os.listdir(BASE_PATH)
    for dirname in dirpath:
        new_path = os.path.join(BASE_PATH, dirname)
        if not os.path.exists(f"{output_path}/{dirname}"):
            os.makedirs(f"{output_path}/{dirname}")
        analyze_project(new_path, f"{output_path}/{dirname}")
        print(f"Analyzed {dirname}")

if __name__ == "__main__":
   # projects_analysis("./dataset/projects", "./projects_analysis/output")
   analyze_project("./examples", "./output/")