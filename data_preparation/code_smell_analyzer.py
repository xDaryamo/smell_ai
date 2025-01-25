import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from components.inspector import Inspector


class CodeSmellAnalyzer:
    """
    Class to analyze code smells in functions extracted from a dataset.
    This class uses the Inspector class to detect code smells in
    individual functions and categorizes functions as clean or smelly.

    Attributes:
        dataset_path (str): Path to the dataset JSON file.
        output_dir (str): Directory to save results.
        max_workers (int): Maximum number of threads for parallelization.
        log_interval (int): Number of functions to
            process before logging progress.
        inspector (Inspector): An instance of the
            Inspector class for analyzing code.
        clean_functions (list): List of functions without code smells.
        smelly_functions (list): List of functions with detected code smells.
        file_cache (dict): Cache to store inspection results for files.
    """

    def __init__(
        self, dataset_path, output_dir, max_workers=4, log_interval=100
    ):
        """
        Initialize the analyzer with the dataset path and output directory.

        Args:
            dataset_path (str): Path to the dataset JSON file.
            output_dir (str): Directory to save results.
            max_workers (int): Maximum number of threads for parallelization.
            log_interval (int): Number of functions to
                process before logging progress.
        """
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.log_interval = log_interval

        os.makedirs(output_dir, exist_ok=True)
        self.inspector = Inspector(output_path=output_dir)
        self.clean_functions = []
        self.smelly_functions = []
        self.file_cache = {}  # Cache to store inspection results for files

        # Setup logging for console only
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def load_dataset(self):
        """
        Load the dataset from the JSON file.

        This method reads the dataset from the specified JSON file and
        stores it as an instance attribute for further processing.
        """
        with open(self.dataset_path, "r") as f:
            self.dataset = json.load(f)

    def analyze_function_in_file(self, function_data):
        """
        Analyze a function by analyzing the entire file and filtering results.

        This method inspects a specific function within its file, checks if it
        contains code smells, and returns the results.

        Args:
            function_data (dict): Function data containing
                file_path, function_name, and code.

        Returns:
            dict: Result indicating if the function is smelly and its smells.
        """
        file_path = function_data["file_path"]

        # Use cache if the file has already been inspected
        if file_path not in self.file_cache:
            try:
                self.file_cache[file_path] = self.inspector.inspect(file_path)
            except Exception as e:
                self.logger.error(f"Error analyzing file {file_path}: {e}")
                return None  # Skip this function

        results = self.file_cache[file_path]
        function_smells = results[
            (results["function_name"] == function_data["function_name"])
        ]

        if not function_smells.empty:
            unique_labels = list(
                set(
                    item["label"]
                    for item in function_smells.to_dict(orient="records")
                )
            )
            return {
                "code": function_data["code"],
                "labels": unique_labels,
            }
        else:
            return {
                "code": function_data["code"],
                "labels": ["No Smell"],
            }

    def analyze_dataset_parallel(self):
        """
        Analyze the entire dataset of functions in parallel.

        This method uses multi-threading to analyze functions from the dataset
        concurrently, categorizing them as clean or smelly.

        Returns:
            tuple: Lists of clean and smelly functions.
        """
        self.load_dataset()

        clean_functions = []
        smelly_functions = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_function = {
                executor.submit(
                    self.analyze_function_in_file, function_data
                ): function_data
                for function_data in self.dataset
            }

            for i, future in enumerate(
                as_completed(future_to_function), start=1
            ):
                function_data = future_to_function[future]
                try:
                    result = future.result()
                    if result is not None:  # Only process non-None results
                        if "No Smells" in result["labels"]:
                            clean_functions.append(result)
                        else:
                            smelly_functions.append(result)
                except Exception as e:
                    self.logger.error(
                        f"Error analyzing function "
                        f"{function_data['function_name']} "
                        f"in file {function_data['file_path']}: {e}"
                    )

                # Log progress every `log_interval` functions
                if i % self.log_interval == 0 or i == len(self.dataset):
                    self.logger.info(
                        f"Processed {i}/{len(self.dataset)} functions..."
                    )

        return clean_functions, smelly_functions

    def save_results(self, clean_functions, smelly_functions):
        """
        Save clean and smelly functions to JSON files.

        This method saves the analyzed functions to separate JSON files
        for clean and smelly functions.

        Args:
            clean_functions (list): List of clean functions.
            smelly_functions (list): List of smelly functions.
        """
        clean_path = os.path.join(self.output_dir, "clean_functions.json")
        smelly_path = os.path.join(self.output_dir, "smelly_functions.json")

        with open(clean_path, "w") as f:
            json.dump(clean_functions, f, indent=4)

        with open(smelly_path, "w") as f:
            json.dump(smelly_functions, f, indent=4)

        self.logger.info(f"Results saved: {clean_path}, {smelly_path}")

    def run(self):
        """
        Run the analysis process.

        This method orchestrates the entire process: loading the dataset,
        analyzing the functions, and saving the results.
        """
        self.logger.info("Starting dataset analysis...")
        clean_functions, smelly_functions = self.analyze_dataset_parallel()
        self.save_results(clean_functions, smelly_functions)
        self.logger.info(
            f"Analysis completed. Clean functions: {len(clean_functions)}, "
            f"Smelly functions: {len(smelly_functions)}"
        )


if __name__ == "__main__":
    # Define paths for the dataset and output
    dataset_path = "datasets/function_extracted.json"
    output_dir = "datasets/output_analysis"

    # Initialize and run the analyzer
    analyzer = CodeSmellAnalyzer(dataset_path, output_dir, max_workers=16)
    analyzer.run()
