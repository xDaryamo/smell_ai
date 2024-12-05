import os
import pandas as pd

class ModelExtractor:
    def __init__(self, models_path: str, tensors_path: str) -> None:
        self.models_path = models_path
        self.tensors_path = tensors_path
        self.model_dict = None
        self.tensor_operations_dict = None

    def load_model_dict(self) -> dict[str, str]:
        """
        Loads the model dictionary from a CSV file.
        """
        self.model_dict = pd.read_csv(self.models_path).to_dict(orient='list')
        return self.model_dict

    def load_tensor_operations_dict(self) -> dict[str, str]:
        """
        Loads the tensor operations dictionary from a CSV file.
        """
        tensors_df = pd.read_csv(self.tensors_path)
        tensors_df = tensors_df[tensors_df['number_of_tensors_input'] > 1]
        self.tensor_operations_dict = tensors_df.to_dict(orient='list')
        return self.tensor_operations_dict

    def check_model_method(self, model: str, libraries: list[str]) -> bool:
        """
        Checks if the given model belongs to any of the provided libraries.
        """
        if not self.model_dict:
            raise ValueError("Model dictionary not loaded. Call `load_model_dict` first.")
        for lib in libraries:
            if lib in self.model_dict['library']:
                for model_part in self.model_dict['method']:
                    if model_part == model and lib in self.model_dict['library']:
                        return True
        return False
