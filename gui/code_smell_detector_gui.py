import os
import sys
import tkinter as tk
from tkinter import filedialog
from cli.file_utils import FileUtils
from cli.project_analyzer import ProjectAnalyzer
from gui.textbox_redirect import TextBoxRedirect


class CodeSmellDetectorGUI:
    """
    The main GUI for the AI-specific Code Smells Detector application.
    """

    def __init__(self, master):
        self.master = master
        self.setup_gui()
        self.configure_stdout()
        self.project_analyzer = None

    def setup_gui(self):
        """
        Sets up the GUI layout and components.
        """
        self.master.title("AI-Specific Code Smells Detector")
        self.master.geometry("500x300")

        # Input Path Selection
        self.input_label = tk.Label(self.master, text="Input Path:")
        self.input_label.grid(row=0, column=0, sticky="w")

        self.input_path = tk.Label(self.master, text="No path selected", anchor="w")
        self.input_path.grid(row=0, column=1, sticky="w")

        self.input_button = tk.Button(
            self.master,
            text="Choose Input Folder",
            bg="lightblue",
            command=self.choose_input_path,
        )
        self.input_button.grid(row=0, column=2, padx=5)

        # Output Path Selection
        self.output_label = tk.Label(self.master, text="Output Path:")
        self.output_label.grid(row=1, column=0, sticky="w")

        self.output_path = tk.Label(self.master, text="No path selected", anchor="w")
        self.output_path.grid(row=1, column=1, sticky="w")

        self.output_button = tk.Button(
            self.master,
            text="Choose Output Folder",
            bg="lightblue",
            command=self.choose_output_path,
        )
        self.output_button.grid(row=1, column=2, padx=5)

        # Walker Selection
        self.walker_label = tk.Label(self.master, text="Select number of walkers:")
        self.walker_label.grid(row=2, column=0, sticky="w")

        self.walker_picker = tk.Spinbox(self.master, from_=1, to=10, width=5)
        self.walker_picker.grid(row=2, column=1, sticky="w")

        # Parallel Checkbox
        self.parallel_var = tk.BooleanVar()
        self.parallel_check = tk.Checkbutton(
            self.master, text="Parallel", variable=self.parallel_var
        )
        self.parallel_check.grid(row=3, column=0, sticky="w")

        # Resume Checkbox
        self.resume_var = tk.BooleanVar()
        self.resume_check = tk.Checkbutton(
            self.master, text="Resume", variable=self.resume_var
        )
        self.resume_check.grid(row=3, column=1, sticky="w")

        # Output Textbox
        self.output_textbox = tk.Text(self.master, height=8, width=50, state="disabled")
        self.output_textbox.grid(row=4, column=0, columnspan=3, pady=10, sticky="nsew")
        self.output_textbox.bind("<Key>", self.disable_key_press)

        # Run and Exit Buttons
        self.run_button = tk.Button(
            self.master, text="Run", bg="lightgreen", command=self.run_program
        )
        self.run_button.grid(row=5, column=0, pady=5)

        self.exit_button = tk.Button(
            self.master, text="Exit", bg="pink", command=self.master.quit
        )
        self.exit_button.grid(row=5, column=2, pady=5)

        # Grid Configuration
        self.master.grid_rowconfigure(4, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

    def configure_stdout(self):
        """
        Redirects stdout to the GUI Text widget.
        """
        output_redirect = TextBoxRedirect(self.output_textbox)
        sys.stdout = output_redirect

    def disable_key_press(self, event):
        """
        Disables user input in the output Text widget.
        """
        return "break"

    def choose_input_path(self):
        """
        Opens a folder selection dialog for input path.
        """
        path = filedialog.askdirectory()
        if path:
            self.input_path.configure(text=path)

    def choose_output_path(self):
        """
        Opens a folder selection dialog for output path.
        """
        path = filedialog.askdirectory()
        if path:
            self.output_path.configure(text=path)

    def run_program(self):
        """
        Executes the analysis program with selected parameters.
        """
        input_path = self.input_path.cget("text")
        output_path = self.output_path.cget("text")
        num_walkers = int(self.walker_picker.get())
        is_parallel = self.parallel_var.get()
        is_resume = self.resume_var.get()

        # Validate paths
        if input_path == "No path selected" or output_path == "No path selected":
            print("Error: Please select valid input and output paths.")
            return

        print(f"Input Path: {input_path}")
        print(f"Output Path: {output_path}")
        print(f"Number of Walkers: {num_walkers}")
        print(f"Parallel Execution: {is_parallel}")
        print(f"Resume Execution: {is_resume}")

        self.project_analyzer = ProjectAnalyzer(output_path)
        self.project_analyzer.setup_inspector(
            "obj_dictionaries/dataframes.csv",
            "obj_dictionaries/models.csv",
            "obj_dictionaries/tensors.csv",
        )

        try:
            # Check if the input is a single project or multiple projects
            if os.path.isdir(input_path):
                print("Analyzing project(s)...")
                self.project_analyzer.projects_analysis(
                    base_path=input_path,
                    max_workers=num_walkers,
                    resume=is_resume,
                    parallel=is_parallel,
                )

            else:
                print("Error: Input path must be a directory.")
        except Exception as e:
            print(f"An error occurred during analysis: {e}")
