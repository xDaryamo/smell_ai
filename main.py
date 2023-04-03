import os
import ast

from libraries import extract_libraries
from APISpecific import dataframe_conversion_api_misused, Chain_Indexing


def analyze_project(project_path):

    for dirpath, dirnames, filenames in os.walk(project_path):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, "r") as file:
                    source = file.read()
                    tree = ast.parse(source)
                    libraries = extract_libraries(tree)
                    # Visita i nodi dell'albero dell'AST alla ricerca di funzioni
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            print(Chain_Indexing(libraries, filename, node))

        for dirname in dirnames:
            new_path = os.path.join(dirpath, dirname)
            analyze_project(new_path)

analyze_project("/Users/broke31/Desktop/Machine_Learning_Projects/test/")
