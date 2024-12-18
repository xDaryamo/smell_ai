import os

from data_preparation.function_extractor import FunctionExtractor


class DirectoryProcessor:
    """
    A class to traverse directories and process Python files.
    """

    def __init__(self, root_directory):
        """
        Initializes the DirectoryProcessor with the root directory.
        Args:
            root_directory (str): Directory to search for Python files.
        """
        self.root_directory = root_directory
        self.all_functions = []

    def process_files(self):
        """
        Traverses the directory and processes all relevant Python files.
        """
        for root, _, files in os.walk(self.root_directory):
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    file_path = os.path.join(root, file)
                    print(f"Processing: {file_path}")
                    extractor = FunctionExtractor(file_path)
                    extractor.parse_file()
                    self.all_functions.extend(extractor.get_functions())

    def get_all_functions(self):
        """
        Returns all extracted functions.
        """
        return self.all_functions
