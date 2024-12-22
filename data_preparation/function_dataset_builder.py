import os
import json
import ast
import logging
from concurrent.futures import ThreadPoolExecutor
from charset_normalizer import detect


class FunctionDatasetBuilder:
    def __init__(
        self,
        repo_path,
        libraries=["pandas", "numpy", "torch", "tensorflow", "sklearn"],
    ):
        """
        Initialize the FunctionDatasetBuilder.

        :param repo_path: Path to the repository
        or root directory of repositories.
        :param libraries: List of ML-related libraries
        to filter files by relevance.
        """
        self.repo_path = repo_path
        self.libraries = libraries

    def get_python_files(self):
        """
        Recursively find all Python files in the repository.

        :return: List of Python file paths.
        """
        logging.info("Scanning repository for Python files...")
        python_files = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        logging.info(f"Found {len(python_files)} Python files.")
        return python_files

    def is_ml_related(self, file_path):
        """
        Check if a Python file is related to
        machine learning by analyzing imports.

        :param file_path: Path to the Python file.
        :return: True if the file contains
        ML-related libraries, False otherwise.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                is_related = any(lib in content for lib in self.libraries)
                if is_related:
                    logging.info(f"File {file_path} is ML-related.")
                return is_related
        except Exception as e:
            logging.warning(f"Could not read file {file_path}: {e}")
            return False

    def extract_functions(self, file_path):
        """
        Extract all functions from a Python file.

        :param file_path: Path to the Python file.
        :return: List of dictionaries representing functions.
        """
        functions = []
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read()
                detected = detect(raw_data)
                encoding = detected.get("encoding", "utf-8")
                content = raw_data.decode(encoding)
        except Exception as e:
            logging.warning(f"Failed to read file {file_path}: {e}")
            return []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(
                        {
                            "function_name": node.name,
                            "start_line": node.lineno,
                            "end_line": getattr(node, "end_lineno", None),
                            "code": ast.get_source_segment(content, node),
                            "file_path": file_path,
                        }
                    )
            if functions:
                logging.info(
                    f"Extracted {len(functions)} functions from {file_path}."
                )
        except SyntaxError as e:
            logging.warning(f"Syntax error in file {file_path}: {e}")
        except Exception as e:
            logging.warning(f"Error parsing file {file_path}: {e}")
        return functions

    def build_dataset(self):
        """
        Build a dataset of functions from ML-related Python files.

        :return: List of dictionaries representing the dataset.
        """
        logging.info("Starting dataset build process...")
        dataset = []
        python_files = self.get_python_files()

        # Filter files in parallel
        logging.info("Filtering ML-related Python files...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            ml_files_flags = list(
                executor.map(self.is_ml_related, python_files)
            )
        ml_files = [
            file for file, is_ml in zip(python_files, ml_files_flags) if is_ml
        ]
        logging.info(f"Identified {len(ml_files)} ML-related Python files.")

        # Extract functions in parallel
        logging.info("Extracting functions from ML-related files...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self.extract_functions, ml_files))

        for functions in results:
            dataset.extend(functions)

        logging.info(f"Extracted {len(dataset)} functions in total.")
        return dataset

    def save_dataset(self, dataset, output_path="partial_dataset.json"):
        """
        Save the dataset to a JSON file.

        :param dataset: Dataset to save.
        :param output_path: Path to the JSON file.
        """
        logging.info(f"Saving dataset to {output_path}...")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=4)
        logging.info(f"Dataset saved successfully to {output_path}.")


# Esempio di utilizzo
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    builder = FunctionDatasetBuilder(repo_path="datasets/raw")
    dataset = builder.build_dataset()
    builder.save_dataset(dataset, "datasets/partial_dataset.json")
    print("Dataset created and saved as partial_dataset.json.")
