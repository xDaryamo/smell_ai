from abc import ABC, abstractmethod
import ast


class Smell(ABC):
    """
    Abstract base class for all code smells.
    Defines the interface for smell detection.
    """

    def __init__(self, name: str, description: str):
        """
        Initializes the Smell with its name and description.

        :param name: Name of the smell.
        :param description: Description of the smell.
        """
        self.name = name
        self.description = description

    @abstractmethod
    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any], filename: str
    ) -> list[dict[str, any]]:
        """
        Structure of `extracted_data`:
        ------------------------------
        - `libraries` (list[str]): List of all libraries used in the code
            (e.g., ["pandas as pd", "numpy as np", "tensorflow as tf"]).
        - `library_aliases` (dict[str, str]): Mapping of library names to their aliases
            (e.g., {"pandas": "pd", "numpy": "np", "tensorflow": "tf"}).
        - `variables` (list[str]): A list of all variables found in the code
            (e.g., ["df", "data", "model", "tensor"]).
        - `dataframe_variables` (list[str]): List of variables identified as Pandas DataFrames
            (e.g., ["df", "data"]).
        - `lines` (dict[int, str]): Mapping of line numbers to the corresponding source code
            (e.g., {1: "import pandas as pd", 2: "df['new_column'] = 0"}).
        - `dataframe_methods` (list[str]): List of methods relevant to DataFrames
            (e.g., ["drop", "rename", "merge", "append"]).
        - `tensor_operations` (list[str]): List of tensor operations relevant for deep learning
            (e.g., ["dot", "matmul", "transpose"]).
        - `models` (list[str]): List of variables identified as machine learning models
            (e.g., ["model", "regressor", "classifier"]).
        - `model_methods` (dict[str, list[str]]): Dictionary of ML/DL methods with their corresponding libraries
            (e.g., {"tensorflow": ["fit", "evaluate", "predict"], "sklearn": ["fit", "score"]}).

        Example of `extracted_data`:
        ----------------------------
        {
            "libraries": ["pandas as pd", "numpy as np", "tensorflow as tf"],
            "library_aliases": {"pandas": "pd", "numpy": "np", "tensorflow": "tf"},
            "variables": ["df", "data", "model", "tensor"],
            "dataframe_variables": ["df", "data"],
            "lines": {
                1: "import pandas as pd",
                2: "df['new_column'] = 0",
                3: "model.fit(X, y)"
            },
            "dataframe_methods": ["drop", "rename", "merge", "append"],
            "tensor_operations": ["dot", "matmul", "transpose"],
            "models": ["model", "regressor", "classifier"],
            "model_methods": {
                "tensorflow": ["fit", "evaluate", "predict"],
                "sklearn": ["fit", "score"]
            }
        }

        :param filename: Name of the file being analyzed.

        :return: A list of dictionaries containing detected smells.
        """
        pass

    def format_smell(self, line: int, additional_info: str = "") -> dict[str, any]:
        """
        Formats a detected smell into a standardized dictionary.

        :param line: Line number where the smell is detected.
        :param additional_info: Optional additional information about the smell.
        :return: A dictionary containing formatted smell data.
        """
        return {
            "name": self.name,
            "line": line,
            "description": self.description,
            "additional_info": additional_info,
        }
