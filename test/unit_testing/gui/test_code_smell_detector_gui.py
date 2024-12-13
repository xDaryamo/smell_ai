import sys
import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from gui.code_smell_detector_gui import CodeSmellDetectorGUI


class TestCodeSmellDetectorGUI(unittest.TestCase):
    def setUp(self):
        """
        Create a tkinter root window and initialize the CodeSmellDetectorGUI.
        """
        self.root = tk.Tk()
        self.gui = CodeSmellDetectorGUI(self.root)

    def tearDown(self):
        """
        Destroy the tkinter root window after each test.
        """
        sys.stdout = sys.__stdout__
        self.root.quit()
        self.root.update()
        self.root.destroy()

    @patch("tkinter.filedialog.askdirectory")
    def test_choose_input_path(self, mock_askdirectory):
        """
        Test the `choose_input_path` method to ensure the input path label is updated.
        """
        # Mock the return value of askdirectory
        mock_askdirectory.return_value = "/mock/input/path"

        # Simulate button click
        self.gui.choose_input_path()

        # Check if the input path label is updated
        self.assertEqual(self.gui.input_path.cget("text"), "/mock/input/path")

    @patch("tkinter.filedialog.askdirectory")
    def test_choose_output_path(self, mock_askdirectory):
        """
        Test the `choose_output_path` method to ensure the output path label is updated.
        """
        # Mock the return value of askdirectory
        mock_askdirectory.return_value = "/mock/output/path"

        # Simulate button click
        self.gui.choose_output_path()

        # Check if the output path label is updated
        self.assertEqual(self.gui.output_path.cget("text"), "/mock/output/path")

    @patch("sys.stdout", new_callable=MagicMock)
    def test_run_program_missing_paths(self, mock_stdout):
        """
        Test the `run_program` method when input or output paths are missing.
        """
        self.gui.input_path.configure(text="No path selected")
        self.gui.output_path.configure(text="No path selected")

        self.gui.run_program()

        # Check that the error message was printed
        output = "".join([call[0][0] for call in mock_stdout.write.call_args_list])
        self.assertIn("Error: Please select valid input and output paths.", output)

    def test_disable_key_press(self):
        """
        Test that key presses are disabled in the output Text widget.
        """
        event = MagicMock()
        result = self.gui.disable_key_press(event)

        # Assert that the "break" string is returned to block the event
        self.assertEqual(result, "break")

    def test_gui_layout(self):
        """
        Test that the GUI layout contains the expected widgets.
        """
        widgets = [
            self.gui.input_label,
            self.gui.input_button,
            self.gui.output_label,
            self.gui.output_button,
            self.gui.walker_picker,
            self.gui.parallel_check,
            self.gui.resume_check,
            self.gui.run_button,
            self.gui.exit_button,
            self.gui.output_textbox,
        ]

        for widget in widgets:
            self.assertTrue(widget.winfo_exists())  # Assert widget exists in the GUI
