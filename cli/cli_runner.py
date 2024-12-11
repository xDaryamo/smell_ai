import argparse
import os
import sys
from cli.file_utils import FileUtils
from cli.project_analyzer import ProjectAnalyzer


class CodeSmileCLI:
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
        print("Starting analysis with the following configuration:")
        print(f"Input folder: {self.args.input}")
        print(f"Output folder: {self.args.output}")
        print(f"Parallel execution: {self.args.parallel}")
        print(f"Resume execution: {self.args.resume}")
        print(f"Analyze multiple projects: {self.args.multiple}")

        if self.args.input is None or self.args.output is None:
            print("Error: Please specify both input and output folders.")
            exit(1)

        # Clean or create the output folder
        if not self.args.resume:
            self.analyzer.output_path = FileUtils.clean_directory(
                self.args.output, "output"
            )

        # Run analysis
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
            total_smells = self.analyzer.analyze_project(self.args.input)
            print(
                f"Analysis completed. Total code smells found: {total_smells}"
            )

        FileUtils.merge_results(
            self.analyzer.output_path,
            os.path.join(self.analyzer.output_path, "overview"),
        )
        print("Analysis results saved successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="Code Smile: AI-specific code smells detector for Python "
        "projects."
    )
    parser.add_argument(
        "--input", type=str, help="Path to the input folder", required=True
    )
    parser.add_argument(
        "--output", type=str, help="Path to the output folder", required=True
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=5,
        help="Number of workers for parallel execution (default: 5)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel execution (default: False)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume previous execution (default: False)",
    )
    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Analyze multiple projects (default: False)",
    )

    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        # SystemExit will be raised automatically for missing arguments
        print("Error: Missing required arguments or invalid input.\n")
        parser.print_help()
        sys.exit(1)

    # Execute main logic
    print("Starting Code Smile analysis...")
    manager = CodeSmileCLI(args)
    manager.execute()


if __name__ == "__main__":
    main()
