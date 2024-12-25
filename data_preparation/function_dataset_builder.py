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

    def _is_file_ml_related(self, file_path):
        """
        Check if a Python file is related to machine learning
        by analyzing imports and function calls using AST.

        :param file_path: Path to the Python file.
        :return: True if the file contains ML-related libraries,
        False otherwise.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Skip files with template placeholders (e.g., {{...}})
            if "{{" in content or "}}" in content:
                logging.warning(f"Skipped template file: {file_path}")
                return False

            # If content is empty or invalid, skip it
            if not content.strip():
                logging.debug(f"File skipped (empty or invalid): {file_path}")
                return False

            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                logging.warning(f"Syntax error in file {file_path}: {e}")
                return False

            ml_related_patterns = [
                "tf.function", "torch.nn.module",
                "keras.layers", "sklearn.metrics"
            ]
            ml_imports = set(self.libraries)
            imported_libraries = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_libraries.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_libraries.add(node.module)

            # Check if any ML-related libraries are imported
            for ml_library in ml_imports:
                if any(ml_library in lib for lib in imported_libraries):
                    return True

            # Look for specific ML-related patterns in the AST
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if (
                        isinstance(node.func, ast.Attribute) and
                        isinstance(node.func.value, ast.Name)
                    ):
                        pattern = f"{node.func.value.id}.{node.func.attr}"
                        if pattern in ml_related_patterns:
                            return True

            logging.debug(f"File skipped (not ML-related): {file_path}")
            return False

        except Exception as e:
            logging.warning(
                f"Could not analyze file {file_path} with AST: {e}"
                )
            return False

    def _contains_ml_keywords(self, function_code):
        """
        Determine if a function contains ML-related
        keywords using AST analysis.

        :param function_code: The code of the function as a string.
        :return: True if ML-related keywords are found, False otherwise.
        """
        keywords = [
            "fit", "predict", "transform", "train", "evaluate", "model",
            "loss", "optimizer", "dataset",
            "dataloader", "backpropagation",
            "gradient", "epoch", "Sequential", "nn.Module",
            "optim", "sklearn",
            "metrics", "layers", "cross_val_score"
        ]
        try:
            tree = ast.parse(function_code)
            for node in ast.walk(tree):
                # Check for keywords in function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        # Direct function call
                        if node.func.id in keywords:
                            return True
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in keywords:  # Method call
                            return True
                # Check for keywords in assignments or other identifiers
                elif isinstance(node, ast.Name) and node.id in keywords:
                    return True
                elif isinstance(node, ast.Attribute):
                    if node.attr in keywords:
                        return True
            return False
        except Exception as e:
            logging.warning(
                f"Error analyzing function for keywords with AST: {e}"
                )
            return False

    def _is_function_ml_related(self, function_code, aliases):
        """
        Determine if a function is ML-related based on
        library aliases.

        :param function_code: The code of the function as a string.
        :param aliases: A dictionary of library aliases.
        :return: True if the function is ML-related, False otherwise.
        """
        libraries_and_aliases = self.libraries + list(aliases.values())
        library_hits = any(
            lib in function_code.lower() for lib in libraries_and_aliases
        )
        if not library_hits:
            logging.debug(
                f"Function skipped (not ML-related): {function_code[:50]}..."
                )
        return library_hits

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

        aliases = ({})
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                # Extract library aliases
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        aliases[alias.asname or alias.name] = alias.name
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        aliases[alias.asname or alias.name] = node.module

                # Extract functions
                if isinstance(node, ast.FunctionDef):
                    function_code = ast.get_source_segment(content, node)
                    if self._is_function_ml_related(function_code, aliases):
                        if self._contains_ml_keywords(function_code):
                            functions.append(
                                {
                                    "function_name": node.name,
                                    "start_line": node.lineno,
                                    "end_line": getattr(
                                        node, "end_lineno", None
                                        ),
                                    "code": function_code,
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
                executor.map(
                    self._is_file_ml_related,
                    python_files)
                    )
        ml_files = [file for file, is_ml in zip(
            python_files, ml_files_flags
            ) if is_ml]
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


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    builder = FunctionDatasetBuilder(repo_path="datasets/raw")
    dataset = builder.build_dataset()
    builder.save_dataset(dataset, "datasets/partial_dataset.json")
    print("Dataset created and saved as partial_dataset.json.")
