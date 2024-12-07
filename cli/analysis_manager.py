import argparse
import os
from cli.file_utils import FileUtils
from cli.project_analyzer import ProjectAnalyzer


class AnalysisManager:
    """Manages the overall analysis workflow."""

    def __init__(self, args):
        """
        Initializes the AnalysisManager with CLI arguments.

        Parameters:
        - args: Parsed CLI arguments.
        """
        self.args = args
        self.analyzer = ProjectAnalyzer(args.output)

    def execute(self):
        """
        Executes the analysis workflow based on CLI arguments.
        """

        self.analyzer.setup_inspector(
            "obj_dictionaries/dataframes.csv",
            "obj_dictionaries/models.csv",
            "obj_dictionaries/tensors.csv",
        )

        if self.args.input is None or self.args.output is None:
            print("Please specify input and output folders.")
            exit(1)

        if not self.args.resume:
            FileUtils.clean_directory(self.args.output)

        if self.args.multiple:
            if self.args.parallel:
                self.analyzer.analyze_projects_parallel(
                    self.args.input, self.args.max_workers
                )
            else:
                self.analyzer.analyze_projects_sequential(
                    self.args.input, resume=self.args.resume
                )
        else:
            self.analyzer.analyze_project(self.args.input)

        FileUtils.merge_results(
            self.args.output, os.path.join(self.args.output, "overview")
        )


def main():
    parser = argparse.ArgumentParser(
        description="Code Smile: AI-specific code smells detector for Python projects."
    )
    parser.add_argument("--input", type=str, help="Path to the input folder")
    parser.add_argument("--output", type=str, help="Path to the output folder")
    parser.add_argument(
        "--max_workers",
        type=int,
        default=5,
        help="Number of workers for parallel execution",
    )
    parser.add_argument(
        "--parallel", default=False, type=bool, help="Enable parallel execution"
    )
    parser.add_argument(
        "--resume", default=False, type=bool, help="Resume previous execution"
    )
    parser.add_argument(
        "--multiple", default=False, type=bool, help="Analyze multiple projects"
    )
    args = parser.parse_args()

    manager = AnalysisManager(args)
    manager.execute()


if __name__ == "__main__":
    main()
