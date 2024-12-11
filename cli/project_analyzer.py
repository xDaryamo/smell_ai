from concurrent.futures import ThreadPoolExecutor
import os
import time
import pandas as pd
from components import inspector
from cli.file_utils import FileUtils


class ProjectAnalyzer:
    """Handles the analysis of Python projects."""

    def __init__(self, output_path: str):
        """
        Initializes the ProjectAnalyzer.

        Parameters:
        - output_path (str): Directory where analysis results will be saved.
        """
        self.output_path = output_path
        self.inspector = inspector.Inspector(output_path)

    def setup_inspector(
        self,
        dataframe_dict_path: str,
        model_dict_path: str,
        tensor_dict_path: str,
    ):
        """
        Sets up the Inspector with necessary dictionaries.

        Parameters:
        - dataframe_dict_path (str): Path to the DataFrame dictionary CSV.
        - model_dict_path (str): Path to the model dictionary CSV.
        - tensor_dict_path (str): Path to the tensor operations CSV.
        """
        self.inspector.setup(
            dataframe_dict_path, model_dict_path, tensor_dict_path
        )

    def analyze_project(self, project_path: str) -> int:
        """
        Analyzes a single project for code smells.

        Parameters:
        - project_path (str): Path to the project to be analyzed.

        Returns:
        - int: Total number of code smells found in the project.
        """
        print(f"Starting analysis for project: {project_path}")

        filenames = FileUtils.get_python_files(project_path)
        col = [
            "filename",
            "function_name",
            "smell_name",
            "line",
            "description",
            "additional_info",
        ]
        to_save = pd.DataFrame(columns=col)
        total_smells = 0

        for filename in filenames:
            if "tests/" not in filename:
                try:
                    result = self.inspector.inspect(filename)

                    smell_count = len(result)
                    total_smells += smell_count
                    if smell_count > 0:
                        print(
                            f"Found {smell_count} code smells in file: "
                            f"{filename}"
                        )
                    to_save = pd.concat([to_save, result], ignore_index=True)
                except (SyntaxError, FileNotFoundError) as e:
                    error_file = os.path.join(self.output_path, "error.txt")
                    os.makedirs(self.output_path, exist_ok=True)
                    with open(error_file, "a") as f:
                        f.write(f"Error in file {filename}: {str(e)}\n")
                    print(f"Error analyzing file: {filename} - {str(e)}")
                    continue

        os.makedirs(self.output_path, exist_ok=True)
        to_save.to_csv(
            os.path.join(self.output_path, "to_save.csv"), index=False
        )

        print(f"Finished analysis for project: {project_path}")
        print(
            "Total code smells found in project "
            f"'{os.path.basename(project_path)}': "
            f"{total_smells}\n"
        )
        return total_smells

    def analyze_projects_sequential(
        self, base_path: str, resume: bool = False
    ):
        """
        Sequentially analyzes multiple projects.

        Parameters:
        - base_path (str): Directory containing projects to be analyzed.
        - resume (bool): Whether to resume from the last analyzed project.
        """
        execution_log_path = os.path.abspath("../config/execution_log.txt")
        os.makedirs("../config", exist_ok=True)

        if not os.path.exists(execution_log_path):
            open(execution_log_path, "w").close()
            resume = False

        last_project = ""
        if resume:
            with open(execution_log_path, "r") as f:
                lines = f.readlines()
                last_project = lines[-1].strip() if lines else ""

        start_time = time.time()
        total_smells = 0

        for dirname in os.listdir(base_path):
            if resume and dirname <= last_project:
                continue

            project_path = os.path.join(base_path, dirname)

            print(f"Analyzing project '{dirname}' sequentially...")
            try:
                project_smells = self.analyze_project(project_path)
                total_smells += project_smells
                print(
                    f"Project '{dirname}' analyzed successfully. Code smells "
                    f"found: {project_smells}\n"
                )

                with open(execution_log_path, "a") as log_file:
                    log_file.write(dirname + "\n")

            except Exception as e:
                print(f"Error analyzing project '{dirname}': {str(e)}\n")

        print(
            f"Sequential execution completed in {time.time() - start_time:.2f}"
            " seconds."
        )
        print(f"Total code smells found in all projects: {total_smells}\n")

    def analyze_projects_parallel(self, base_path: str, max_workers: int):
        """
        Analyzes multiple projects in parallel.

        Parameters:
        - base_path (str): Directory containing projects to be analyzed.
        - max_workers (int): Maximum number of parallel threads.
        """
        start_time = time.time()
        total_smells = 0

        def analyze_and_count_smells(dirname: str):
            nonlocal total_smells
            project_path = os.path.join(base_path, dirname)
            print(f"Analyzing project '{dirname}' in parallel...")
            try:
                project_smells = self.analyze_project(project_path)
                total_smells += project_smells
            except Exception as e:
                print(f"Error analyzing project '{dirname}': {str(e)}\n")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for dirname in os.listdir(base_path):
                executor.submit(analyze_and_count_smells, dirname)

        print(
            f"Parallel execution completed in {time.time() - start_time:.2f} "
            f"seconds."
        )
        print(f"Total code smells found in all projects: {total_smells}\n")

    def projects_analysis(
        self,
        base_path: str,
        max_workers: int = 5,
        resume: bool = False,
        parallel: bool = False,
    ):
        """
        Handles the overall analysis of multiple projects.

        Parameters:
        - base_path (str): Directory containing projects to analyze.
        - max_workers (int): Maximum number of threads for parallel execution.
        - resume (bool): Whether to resume from the last analyzed project.
        - parallel (bool): Whether to enable parallel analysis.
        """
        if parallel:
            print("Running in parallel mode...")
            self.analyze_projects_parallel(base_path, max_workers)
        else:
            print("Running in sequential mode...")
            self.analyze_projects_sequential(base_path, resume)
