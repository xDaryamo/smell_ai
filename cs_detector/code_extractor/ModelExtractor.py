import os
import pandas as pd

class ModelExtractor:
    def __init__(self, models_path: str, tensors_path: str):
        """
        Initializes the ModelExtractor with paths to the model and tensor CSV files.

        Parameters:
        - models_path (str): Path to the CSV file containing model dictionary data.
        - tensors_path (str): Path to the CSV file containing tensor operations data.

        Instance Variables:
        - self.models_path (str): Stores the path to the model dictionary file.
        - self.tensors_path (str): Stores the path to the tensor operations file.
        - self.model_dict (dict[str, str] or None): A dictionary representing model-related data (loaded from CSV).
        - self.tensor_operations_dict (dict[str, str] or None): A dictionary representing tensor operations data (loaded from CSV).
        """
        self.models_path = models_path
        self.tensors_path = tensors_path
        self.model_dict = None
        self.tensor_operations_dict = None

    def load_model_dict(self) -> dict[str, list]:
        """
        Loads the model dictionary from the CSV file specified in `self.models_path`.

        Returns:
        - dict[str, list]: A dictionary where the keys are column names from the CSV and the values are lists of column data.

        Raises:
        - FileNotFoundError: If the CSV file at `self.models_path` cannot be found.
        """
        self.model_dict = pd.read_csv(self.models_path).to_dict(orient='list')
        return self.model_dict

    def load_tensor_operations_dict(self) -> dict[str, list]:
        """
        Loads the tensor operations dictionary from the CSV file specified in `self.tensors_path`.

        Filters out operations that do not involve multiple tensor inputs.

        Returns:
        - dict[str, list]: A dictionary where the keys are column names from the CSV and the values are lists of column data,
                           filtered to include only operations with more than one tensor input.

        Raises:
        - FileNotFoundError: If the CSV file at `self.tensors_path` cannot be found.
        """
        tensors_df = pd.read_csv(self.tensors_path)
        tensors_df = tensors_df[tensors_df['number_of_tensors_input'] > 1]
        self.tensor_operations_dict = tensors_df.to_dict(orient='list')
        return self.tensor_operations_dict

    def check_model_method(self, model: str, libraries: list[str]) -> bool:
        """
        Checks if the specified model belongs to any of the provided libraries.

        Parameters:
        - model (str): The name of the model to check.
        - libraries (list[str]): A list of library names to check against.

        Returns:
        - bool: True if the model belongs to any of the specified libraries; False otherwise.

        Raises:
        - ValueError: If the model dictionary has not been loaded by calling `load_model_dict`.

        Notes:
        - This function checks if `model` exists in the `method` column of the model dictionary and if the corresponding
          library exists in the `library` column of the dictionary.
        """
        if not self.model_dict:
            raise ValueError("Model dictionary not loaded. Call `load_model_dict` first.")
        for lib in libraries:
            if lib in self.model_dict['library']:
                for model_part in self.model_dict['method']:
                    if model_part == model and lib in self.model_dict['library']:
                        return True
        return False
