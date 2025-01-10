import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import UploadPythonPage from "../../app/upload-python/page";
import { detectAi, detectStatic } from "../../utils/api";

// Mock API functions
jest.mock("../../utils/api", () => ({
  detectAi: jest.fn() as jest.Mock<Promise<any>>,  
  detectStatic: jest.fn() as jest.Mock<Promise<any>>, 
}));

describe("UploadPythonPage", () => {
  test("displays the correct file name after file is selected", async () => {
    render(<UploadPythonPage />);

    // Simulate selecting a file
    const file = new File(["test content"], "test_file.py", { type: "text/plain" });
    const fileInput = screen.getByLabelText(/select a python file/i);
    fireEvent.change(fileInput, { target: { files: [file] } });

    // Wait for the file name to appear
    await waitFor(() => {
      expect(screen.getByRole("file-uploader").textContent?.includes("test_file.py"));
    });
  });

  test("toggles analysis mode between AI and Static", () => {
    render(<UploadPythonPage />);

    const aiButton = screen.getByText(/AI-Based/i);
    const staticButton = screen.getByText(/Static Tool/i);

    // Initial mode should be "AI"
    expect(aiButton).toHaveClass("bg-red-500");

    // Switch to "Static" mode
    fireEvent.click(staticButton);
    expect(staticButton).toHaveClass("bg-blue-500");
    expect(aiButton).toHaveClass("bg-gray-200");
  });

test("shows loading state and progress bar when submitting", async () => {
    render(<UploadPythonPage />);

    // Mock the API response
    (detectAi as jest.Mock).mockResolvedValue({
        smells: [
            {
                function_name: "main",
                line: 1,
                smell_name: "Code Smell",
                description: "Unoptimized code",
                additional_info: "",
            },
        ],
    });

    // Mock the FileReader to simulate file.text() behavior
    const mockText = jest.fn().mockResolvedValue("test content");
    global.File.prototype.text = mockText;

    // Simulate file selection and submission
    const file = new File(["test content"], "test_file.py", { type: "text/plain" });
    const fileInput = screen.getByLabelText(/select a python file/i);
    fireEvent.change(fileInput, { target: { files: [file] } });

    const submitButton = screen.getByText(/Upload Code/i);

    await waitFor(() => {
        expect(screen.getByText('Upload and Analyze Python Code')).toBeVisible();
    });

    fireEvent.click(submitButton);

    // Check that the loading state text appears
    await waitFor(() => {
        expect(screen.getByTestId("progress").textContent?.includes("Uploading and analyzing code..."));
    });

    // Wait for the result to update
    await waitFor(() => {
        expect(
            screen.getByText(/Code uploaded and analyzed successfully!/i)
        ).toBeInTheDocument();
    });

    // Ensure that file.text() was called
    expect(mockText).toHaveBeenCalledTimes(1);
});



  test("displays results after analysis", async () => {
    render(<UploadPythonPage />);

    // Mock the API response
    (detectAi as jest.Mock).mockResolvedValue({
      smells: [{ function_name: "main", line: 1, smell_name: "Code Smell", description: "Unoptimized code", additional_info: "" }],
    });

    // Simulate file selection and submission
    const file = new File(["test content"], "test_file.py", { type: "text/plain" });
    const fileInput = screen.getByLabelText(/select a python file/i);
    fireEvent.change(fileInput, { target: { files: [file] } });

    const submitButton = screen.getByText(/Upload Code/i);
    fireEvent.click(submitButton);

    // Wait for the analysis to complete and results to show
    await waitFor(() => {
      expect(screen.getByText(/Smell #1/i)).toBeInTheDocument();
      expect(screen.getByText(/Description:/i).textContent?.includes("Unoptimized code"));
    });
  });

  test("handles API failure gracefully", async () => {
    render(<UploadPythonPage />);

    // Mock the API failure
    (detectAi as jest.Mock).mockRejectedValue(new Error("API failed"));

    // Simulate file selection and submission
    const file = new File(["test content"], "test_file.py", { type: "text/plain" });
    const fileInput = screen.getByLabelText(/select a python file/i);
    fireEvent.change(fileInput, { target: { files: [file] } });

    const submitButton = screen.getByText(/Upload Code/i);
    fireEvent.click(submitButton);

    // Wait for error message to appear
    await waitFor(() => {
      expect(screen.getByText(/Error uploading and analyzing code/i)).toBeInTheDocument();
    });
  });
});
