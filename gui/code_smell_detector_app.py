import tkinter as tk
from gui.code_smell_detector_gui import CodeSmellDetectorGUI


class CodeSmellDetectorApp:
    """
    Application controller for initializing and running the GUI.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.gui = CodeSmellDetectorGUI(self.root)

    def run(self):
        """
        Runs the GUI application.
        """
        self.root.mainloop()
