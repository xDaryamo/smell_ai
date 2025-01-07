"use client";
import { useState } from "react";
import Header from "../../components/HeaderComponent";
import Footer from "../../components/FooterComponent";
import { generateReport } from "../../utils/api";
import { useProjectContext } from "../../components/ProjectContext";

import { jsPDF } from "jspdf";
import autoTable, { jsPDFDocument } from "jspdf-autotable"; 
import { motion } from "framer-motion";

import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

// Types
type Smell = {
  smell_name: string;
  description: string;
  function_name: string;
  line: number;
  additional_info: string;
};

type ChartData = { smell_name: string; filename: string };

export default function ReportGeneratorPage() {
  const { projects } = useProjectContext();
  const [loading, setLoading] = useState<boolean>(false);
  const [chartData, setChartData] = useState<ChartData[] | null>(null);

  const handleGenerateReports = async () => {
    if (projects.length === 0) {
      alert("No projects available. Please add projects before generating reports.");
      return;
    }

    setLoading(true);

    try {
      const formattedProjects = projects.map((project) => ({
        name: project.name || "Unnamed Project",
        data: {
          files: project.files?.map((file) => ({
            name: file.name,
            size: file.size,
            type: file.type || "unknown",
            path: file.webkitRelativePath || "",
          })) || [],
          message: project.data?.message || "No message provided",
          result: project.data?.result || "No result available",
          smells:
            project.data?.smells
              ?.map((smell) => {
                if (typeof smell === "string" && smell === "Static analysis returned no data") {
                  return null;
                } else if (smell && smell.smell_name) {
                  return {
                    smell_name: smell.smell_name,
                    description: smell.description || "No description provided",
                    function_name: smell.function_name || "N/A",
                    line: smell.line || -1,
                    additional_info: smell.additional_info || "N/A",
                  };
                } else {
                  return null;
                }
              })
              .filter((smell) => smell !== null) || [],
        },
      }));

      const result = await generateReport(formattedProjects);
      console.log(result);

      if (result.report_data) {
        const combinedData: ChartData[] = [];
        Object.keys(result.report_data).forEach((projectKey) => {
          const projectData = result.report_data[projectKey];
          projectData.forEach((item: ChartData) => {
            combinedData.push(item);
          });
        });

        setChartData(combinedData);
      } else {
        throw new Error("Failed to retrieve report data.");
      }
    } catch (error) {
      console.error("Error generating reports:", error);
      alert("An error occurred while generating reports. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    if (!chartData) {
      alert("No data available for the report.");
      return;
    }

    const doc = new jsPDF();
    const title = "Smell Analysis Report";
    doc.setFontSize(18);
    doc.text(title, 14, 20);

    let currentY = 30;

    projects.forEach((project) => {
      const projectTitle = project.name || "Unnamed Project";
      doc.setFontSize(14);
      doc.text(`Project: ${projectTitle}`, 14, currentY);
      currentY += 10;

      const projectData = project.data;
      const tableData = projectData.smells?.map((smell: Smell) => [
        smell.smell_name,
        smell.function_name,
        smell.line,
        smell.description,
      ]) || [];

      autoTable(doc, {
        head: [["Smell Name", "Function Name", "Line", "Description"]],
        body: tableData,
        startY: currentY,
      });

      currentY = (doc as jsPDFDocument).lastAutoTable.finalY + 10;
    });

    doc.save("smell_analysis_report.pdf");
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-gray-50 to-gray-200">
      <Header />

      <main className="flex-grow py-16 bg-gradient-to-b from-blue-50 via-blue-100 to-gray-50">
        <div className="max-w-3xl mx-auto p-8 bg-white shadow-xl rounded-2xl border border-gray-200">
          <motion.h1
            className="text-4xl font-extrabold text-blue-700 mb-8 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            Report Generator
          </motion.h1>

          <div className="mb-8">
            <p className="text-lg font-semibold text-gray-700">
              Total Projects Available: {projects.length}
            </p>
          </div>

          <motion.button
            onClick={handleGenerateReports}
            className="w-full bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-800 transition-all"
            disabled={loading}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            {loading ? "Generating Reports..." : "Generate Report"}
          </motion.button>

          {chartData && (
            <motion.div
              id="chart-div"
              className="mt-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <h2 className="text-2xl font-bold text-gray-700 mb-4">Combined Smell Occurrences</h2>

              <Plot
                data={[
                  {
                    type: "bar",
                    x: chartData.map((item) => item.smell_name),
                    y: chartData.map((item) => item.filename),
                    marker: { color: "rgb(31, 119, 180)" },
                  },
                ]}
                layout={{
                  title: "Smell Occurrences for All Projects",
                  xaxis: { title: "Smell Type" },
                  yaxis: { title: "Number of Occurrences" },
                }}
              />

              <motion.button
                onClick={handleDownloadPDF}
                className="mt-4 w-full bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Download Report as PDF
              </motion.button>
            </motion.div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
