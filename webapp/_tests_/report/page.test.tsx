import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ReportGeneratorPage from "../../app/reports/page";
import { useProjectContext } from "../../components/ProjectContext";
import { generateReport } from "../../utils/api";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

// Define a mock for `useProjectContext` hook
jest.mock("../../components/ProjectContext", () => ({
  useProjectContext: jest.fn(),
}));

jest.mock("jspdf-autotable", () => jest.fn().mockImplementation(() => ({
  lastAutoTable: { finalY: 100 }  // Mock `finalY` here
})));

// Mock `generateReport` function
jest.mock("../../utils/api", () => ({
  generateReport: jest.fn(),
}));

// Mock `jsPDF` and `autoTable` (no-op implementations)
jest.mock("jspdf", () => ({
  jsPDF: jest.fn().mockImplementation(() => ({
    setFontSize: jest.fn(),
    text: jest.fn(),
    save: jest.fn(),
  })),
}));

describe("ReportGeneratorPage", () => {
  const mockProjects = [
    {
      name: "Project 1",
      files: [
        { name: "file1.py", size: 100, type: "text/plain", webkitRelativePath: "file1.py" },
      ],
      data: {
        message: "Analysis results",
        smells: [
          {
            smell_name: "Code Smell",
            description: "Unoptimized code",
            function_name: "main",
            line: 1,
            additional_info: "Details",
          },
        ],
      },
    },
  ];

  beforeEach(() => {
    // Mock the `useProjectContext` to return mockProjects
    (useProjectContext as jest.Mock).mockReturnValue({ projects: mockProjects });

    // Mock the `generateReport` function to return resolved value
    (generateReport as jest.Mock).mockResolvedValue({
      report_data: {
        "Project 1": [
          { smell_name: "Code Smell", filename: "file1.py" },
        ],
      },
    });
  });

  it("renders correctly with initial state", () => {
    render(<ReportGeneratorPage />);
    expect(screen.getByText(/Total Projects Available/)).toBeInTheDocument();
    expect(screen.getByText(/Generate Report/)).toBeInTheDocument();
  });

  it("displays loading state while generating report", async () => {
    render(<ReportGeneratorPage />);

    fireEvent.click(screen.getByText(/Generate Report/));

    await waitFor(() => {
      expect(screen.getByText(/Generating Reports.../)).toBeInTheDocument();
    });
  });

  it("handles report generation correctly", async () => {
    render(<ReportGeneratorPage />);

    fireEvent.click(screen.getByText(/Generate Report/));

    await waitFor(() => {
      expect(generateReport).toHaveBeenCalledTimes(2);
      expect(generateReport).toHaveBeenCalledWith([
        {
          name: "Project 1",
          data: {
            files: [{ name: "file1.py", size: 100, type: "text/plain", path: "file1.py" }],
            message: "Analysis results",
            result: "No result available",
            smells: [
              {
                smell_name: "Code Smell",
                description: "Unoptimized code",
                function_name: "main",
                line: 1,
                additional_info: "Details",
              },
            ],
          },
        },
      ]);
      expect(screen.getByText(/Combined Smell Occurrences/)).toBeInTheDocument();
    });
  });

  it("shows an alert if no projects are available", async () => {
    // Update mock to return no projects
    (useProjectContext as jest.Mock).mockReturnValue({ projects: [] });

    // Spy on window.alert
    jest.spyOn(window, "alert").mockImplementation(() => {});

    render(<ReportGeneratorPage />);

    fireEvent.click(screen.getByText(/Generate Report/));

    // Wait for the error handling logic to trigger
    await waitFor(() => {
      // Check that an error alert was shown
      expect(window.alert).toHaveBeenCalledWith("No projects available. Please add projects before generating reports.");
    });
  });

  it("handles errors during report generation", async () => {
    // Mock API error
    (generateReport as jest.Mock).mockRejectedValue(new Error("API error"));

    // Spy on window.alert
    jest.spyOn(window, "alert").mockImplementation(() => {});

    render(<ReportGeneratorPage />);

    fireEvent.click(screen.getByText(/Generate Report/));

    // Wait for the error handling logic to trigger
    await waitFor(() => {
      // Check that an error alert was shown
      expect(window.alert).toHaveBeenCalledWith("An error occurred while generating reports. Please try again.");
    });
  });
});
