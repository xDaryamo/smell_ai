import os
import ast
import pandas as pd
from code_extractor.library_extractor import LibraryExtractor
from code_extractor.model_extractor import ModelExtractor
from code_extractor.dataframe_extractor import DataFrameExtractor
from code_extractor.variable_extractor import VariableExtractor
from components.rule_checker import RuleChecker

class Inspector:
    def __init__(self, output_path: str):
        """
        Initializes the Inspector with the output path for saving detected smells.

        Parameters:
        - output_path (str): Path where detected smells will be saved.
        """
        self.output_path = output_path

        self.rule_checker = None
        self.library_extractor = None
        self.model_extractor = None
        self.dataframe_extractor = None
        self.variable_extractor = None

    def setup(self, dataframe_dict_path: str, model_dict_path: str, tensor_dict_path: str) -> None:
        """
        Sets up the necessary components for the Inspector.

        Parameters:
        - dataframe_dict_path (str): Path to the DataFrame dictionary CSV.
        - model_dict_path (str): Path to the model dictionary CSV.
        - tensor_dict_path (str): Path to the tensor operations CSV.
        - smells (list): List of `Smell` instances to be used by the `RuleChecker`.
        """
        # Initialize the RuleChecker with smells and extractors
        self.rule_checker = RuleChecker(self.output_path)
        self.rule_checker.setup_smells()

        self.variable_extractor = VariableExtractor()
        self.library_extractor = LibraryExtractor()
        self.model_extractor = ModelExtractor(
            models_path=model_dict_path,
            tensors_path=tensor_dict_path,
        )
        self.dataframe_extractor = DataFrameExtractor(
            df_dict_path=dataframe_dict_path,
        )

    def inspect(self, filename: str) -> pd.DataFrame:
        """
        Inspects a file for code smells by parsing it into an AST and applying rules.

        Parameters:
        - filename (str): The name of the file to analyze.

        Returns:
        - pd.DataFrame: A DataFrame containing detected code smells.
        """
        col = ["filename", "smell_name", "line", "description", "additional_info"]
        to_save = pd.DataFrame(columns=col)
        file_path = os.path.abspath(filename)

        try:
            with open(file_path, "rb") as file:
                source = file.read()

            # Parse the file into an AST
            tree = ast.parse(source)
            lines = source.decode('utf-8').splitlines()  

            # Extract libraries
            libraries = self.library_extractor.extract_libraries(tree)
            library_aliases = {
                self.library_extractor.extract_library_name(lib): self.library_extractor.extract_library_as_name(lib)
                for lib in libraries
            }

            self.dataframe_extractor.set_libraries(libraries)

            # Extract variables using VariableExtractor
            set_variables = self.variable_extractor.get_all_set_variables(lines)

            # Extract DataFrame-related variables
            dataframe_variables = self.dataframe_extractor.get_dataframe_variables(set_variables)

            # Load dictionaries
            models = self.model_extractor.load_model_dict()
            model_methods = self.model_extractor.load_model_methods()
            df_dict = self.dataframe_extractor.load_dataframe_dict()
            tensor_operations = self.model_extractor.load_tensor_operations_dict()

            # Combine all extracted data into a unified dictionary
            extracted_data = {
                "libraries": libraries,
                "library_aliases": library_aliases,
                "variables": set_variables,
                "dataframe_variables": dataframe_variables,
                "lines": {node.lineno: source.splitlines()[node.lineno - 1] for node in ast.walk(tree) if hasattr(node, "lineno")},
                "dataframe_methods": df_dict["method"] if isinstance(df_dict["method"], list) else df_dict["method"].tolist(),
                "tensor_operations": tensor_operations["operation"].tolist() if "operation" in tensor_operations else [],
                "models": list(models.keys()),
                "model_methods": model_methods,
            }

            # Traverse the AST and analyze each function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    to_save = self.rule_checker.rule_check(
                        node, extracted_data, filename, to_save
                    )

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error in file {filename}: {e}")
        except SyntaxError as e:
            raise SyntaxError(f"Error in file {filename}: {e}")

        return to_save

