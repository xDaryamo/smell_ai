from collections import defaultdict
import json
import random
import re


class FinalDatasetBuilder:
    def __init__(self, clean_path, smelly_path, injected_path, output_path):
        """
        Initializes the BalancedDatasetBuilder.

        Args:
            clean_path (str): Path to clean functions file.
            smelly_path (str): Path to smelly functions file.
            injected_path (str): Path to injected functions file.
            output_path (str): Path to save the unified dataset.
        """
        self.clean_path = clean_path
        self.smelly_path = smelly_path
        self.injected_path = injected_path
        self.output_path = output_path
        # Mapping to normalize smell names
        self.smell_name_mapping = {
            "hyperparameters_not_explicitly_set": (
                "Hyperparameter Not Explicitly Set"
            ),
            "pytorch_call_method_misused": ("PyTorch Call Method Misused"),
            "gradients_not_cleared_before_backward_propagation": (
                "Gradients Not Cleared Before Backward Propagation"
            ),
            "matrix_multiplication_api_misused": (
                "Matrix Multiplication API Misused"
            ),
            "dataframe_conversion_api_misused": (
                "Dataframe Conversion API Misused"
            ),
            "columns_and_datatype_not_explicitly_set": (
                "Columns and DataType Not Explicitly Set"
            ),
            "in_place_apis_misused": ("In-Place APIs Misused"),
            "unnecessary_iteration": ("Unnecessary Iteration"),
            "empty_column_misinitialization": (
                "Empty Column Misinitialization"
            ),
            "Chain_Indexing": ("Chain Indexing"),
            "nan_equivalence_comparison_misused": (
                "NaN Equivalence Comparison Misused"
            ),
            "deterministic_algorithm_option_not_used": (
                "Deterministic Algorithm Option Not Used"
            ),
            "Pytorch Call Method Misused": ("PyTorch Call Method Misused"),
        }

    @staticmethod
    def load_json(file_path):
        """Load a JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_json(data, file_path):
        """Save data to a JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def extract_python_code(input_string):
        """Extract Python code from a string wrapped in ```python``` blocks."""
        pattern = r"```python\\n(.*?)\\n```"
        match = re.search(pattern, input_string, re.DOTALL)

        if match:
            # Extract code from the block
            python_code = match.group(1)

            # Remove comments from the code
            python_code = re.sub(r"#.*", "", python_code)

            # Remove empty lines caused by comment removal
            python_code = "\n".join(
                [line for line in python_code.splitlines() if line.strip()]
            )

            return python_code

        # If no match, assume the input is plain code and process it
        else:
            # Remove comments and clean up the input string
            input_string = re.sub(r"#.*", "", input_string)
            input_string = "\n".join(
                [line for line in input_string.splitlines() if line.strip()]
            )

            return input_string

    def normalize_smell_names(self, smells):
        """Normalize smell names based on the defined mapping."""
        return [self.smell_name_mapping.get(smell, smell) for smell in smells]

    def process_clean_functions(self, clean_functions, target_clean):
        """Add 'No Smell' labels to clean functions."""
        sampled = random.sample(clean_functions, target_clean)
        return [
            {"code": func["code"], "labels": ["No Smell"]} for func in sampled
        ]

    def process_smelly_functions(self, smelly_functions):
        """Extract and normalize labels from smelly functions."""
        processed = []
        for func in smelly_functions:
            labels = [smell["smell_name"] for smell in func["smells"]]
            normalized_labels = self.normalize_smell_names(labels)
            processed.append(
                {
                    "code": func["function_data"]["code"],
                    "labels": normalized_labels,
                }
            )
        return processed

    def process_injected_functions(self, injected_functions):
        """Clean and normalize labels for injected functions."""
        processed = []
        for func in injected_functions:
            code = self.extract_python_code(func["code"])

            # Remove comments
            code = re.sub(r"#.*", "", code)

            # Remove empty lines caused by comment removal
            code = "\n".join(
                [line for line in code.splitlines() if line.strip()]
            )

            # Normalize labels
            normalized_labels = self.normalize_smell_names(func["labels"])

            processed.append({"code": code, "labels": normalized_labels})

        return processed

    def balance_per_smell(self, smelly, injected, target_per_smell):
        """
        Balance the dataset to include a specific number of samples per smell.

        Args:
            smelly (list): Naturally smelly functions.
            injected (list): Functions with injected smells.
            target_per_smell (int): Target number of samples per smell.

        Returns:
            list: Balanced dataset.
        """
        # Create a dictionary to store functions by smell
        smell_to_samples = defaultdict(list)

        # Group functions by smells
        for sample in smelly + injected:
            for label in sample["labels"]:
                smell_to_samples[label].append(sample)

        # Track already included samples
        included_samples = set()
        balanced = []

        # Balance samples for each smell
        for smell, samples in smell_to_samples.items():
            selected = []
            for sample in samples:
                if sample["code"] not in included_samples:
                    selected.append(sample)
                    included_samples.add(sample["code"])
                    if len(selected) >= target_per_smell:
                        break

            balanced.extend(selected)
            print(f"Added {len(selected)} samples for smell: {smell}")

        return balanced

    def build_dataset(self, target_clean, target_per_smell):
        """
        Build a unified and balanced dataset.

        Args:
            target_clean (int): Number of clean samples to include.
            target_per_smell (int): Target number of samples per smell.
        """
        # Load datasets
        clean_functions = self.load_json(self.clean_path)
        smelly_functions = self.load_json(self.smelly_path)
        injected_functions = self.load_json(self.injected_path)

        # Process clean functions
        clean_processed = self.process_clean_functions(
            clean_functions, target_clean
        )

        # Process smelly and injected functions
        smelly_processed = self.process_smelly_functions(smelly_functions)
        injected_processed = self.process_injected_functions(
            injected_functions
        )

        # Balance smelly and injected functions per smell
        balanced_smells = self.balance_per_smell(
            smelly_processed, injected_processed, target_per_smell
        )

        # Combine datasets
        final_dataset = clean_processed + balanced_smells
        random.shuffle(final_dataset)

        # Summary of the dataset
        total_clean = len(clean_processed)
        total_smelly = len(smelly_processed)
        total_injected = len(injected_processed)
        total_balanced = len(balanced_smells)
        total_final = len(final_dataset)

        # Count occurrences of each smell (handle multilabel)
        smell_counts = defaultdict(int)
        for sample in balanced_smells:
            for label in sample["labels"]:
                smell_counts[label] += 1

        print("Dataset summary:")
        print(f"  Total clean functions: {total_clean}")
        print(f"  Total smelly functions: {total_smelly}")
        print(f"  Total injected functions: {total_injected}")
        print(f"  Total balanced samples: {total_balanced}")
        print(f"  Final dataset size: {total_final}")
        print("  Smell occurrences:")
        for smell, count in smell_counts.items():
            print(f"    {smell}: {count}")

        # Save the final dataset
        self.save_json(final_dataset, self.output_path)
        print(f"Unified and balanced dataset saved to {self.output_path}")


if __name__ == "__main__":
    # Paths to input files
    clean_path = "datasets/output_analysis/clean_functions.json"
    smelly_path = "datasets/output_analysis/smelly_functions.json"
    injected_path = "datasets/output_analysis/injected_functions.json"

    # Path to save the unified dataset
    output_path = "datasets/unified_dataset_balanced.json"

    # Initialize the builder
    builder = FinalDatasetBuilder(
        clean_path, smelly_path, injected_path, output_path
    )

    # Build the dataset
    builder.build_dataset(target_clean=5000, target_per_smell=300)
