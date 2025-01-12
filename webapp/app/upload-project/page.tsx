"use client";

import { useState } from "react";
import Header from "../../components/HeaderComponent";
import Footer from "../../components/FooterComponent";
import Project from "../../components/ProjectComponent";
import { useProjectContext } from "../../components/ProjectContext";
import { detectAi, detectStatic } from "../../utils/api";
import { motion } from "framer-motion";

export default function UploadProjectPage() {
  const { projects, addProject, updateProject } = useProjectContext();
  const [analysisMode, setAnalysisMode] = useState<"AI" | "Static">("AI");

  
  const handleSubmitAll = async () => {
  // Set loading state for all projects
  projects.forEach((_, index) => {
    updateProject(index, {
      files: null,
      isLoading: true,
      data: { files: null, message: "Uploading and analyzing the project...", result: null, smells: null },
    });
  });

  try {
    const codeSnippets = projects.flatMap((project) =>
      project.files
        ? project.files.map(async (file) => {
            const content = await file.text();
            return { file, content };
          })
        : []
    );

    const resolvedSnippets = await Promise.all(codeSnippets);

    const results = await Promise.all(
      resolvedSnippets.map((snippet) =>
        analysisMode === "AI" ? detectAi(snippet.content) : detectStatic(snippet.content)
      )
    );

    let resultIndex = 0;
    projects.forEach((project, index) => {
      if (project.files) {
        const projectFiles = Array.from(project.files).filter((file) => file.name.endsWith(".py"));
        const projectResults = results.slice(resultIndex, resultIndex + projectFiles.length);
        resultIndex += projectFiles.length;

       const resultString = projectResults
        .map((res, fileIndex) => {
          const fileName = projectFiles[fileIndex].name;
          const smells = Array.isArray(res.smells) ? res.smells : [];
          return `File: ${fileName}\n` + smells
            .map((smell) =>
              `Function: ${smell.function_name ?? 'N/A'}\n` + 
              `Line: ${smell.line}\nSmell: ${smell.smell_name}\nDescription: ${smell.description}\nAdditional Info: ${smell.additional_info}`
            )
            .join("\n\n");
        })
        .join("\n\n");

        updateProject(index, {
          files: projectFiles.map((file) => file), 
          data: {
            files: projectFiles.map((file) => file.name),
            message: "Projects successfully analyzed!",
            result: resultString,
            smells: projectResults.flatMap((result) => result.smells) || [],
          },
          isLoading: false,
        });
        console.log(results)
      } else {
        updateProject(index, {
          files: null,
          data: {
            files: null,
            message: "No valid files to analyze.",
            result: null,
            smells: [],
          },
          isLoading: false,
        });
      }
    });
  } catch (error) {
    console.error("Error during project analysis:", error);
    // Update the state of all projects in case of error
    projects.forEach((_, index) => {
      updateProject(index, {
        files: null, 
        data: {
          files: null,  
          message: "Error analyzing project.",
          result: null,
          smells: [],
        },
        isLoading: false,
      });
    });
  }
};



  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-blue-100 to-gray-200">
      <Header />

      <main className="flex-grow py-16 bg-gradient-to-b from-purple-50 via-indigo-100 to-gray-50">
        <div className="max-w-4xl mx-auto p-8 bg-white shadow-2xl rounded-3xl border border-gray-200">
          <motion.h1
            className="text-5xl font-extrabold text-blue-700 mb-8 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            Upload and Analyze Projects
          </motion.h1>

          {/* Analysis Mode Toggle */}
          <motion.div
            className="mb-8 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <label className="block mb-4 font-semibold text-xl text-gray-700">Select Analysis Mode:</label>
            <div className="flex justify-center space-x-6">
              <motion.button
                onClick={() => setAnalysisMode("AI")}
                className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${analysisMode === "AI" ? "bg-red-600 text-white shadow-xl" : "bg-gray-200 text-gray-700 hover:bg-gray-300"} hover:scale-105`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                AI-Based
              </motion.button>
              <motion.button
                onClick={() => setAnalysisMode("Static")}
                className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${analysisMode === "Static" ? "bg-blue-600 text-white shadow-xl" : "bg-gray-200 text-gray-700 hover:bg-gray-300"} hover:scale-105`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Static Tool
              </motion.button>
            </div>
          </motion.div>

          {/* Add Project Button */}
          <motion.button
            onClick={addProject}
            className="w-full bg-green-600 text-white px-6 py-3 rounded-xl shadow-xl font-semibold hover:bg-green-700 transition-all duration-300 mb-6 transform hover:scale-105"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Add Project
          </motion.button>

          {/* Project List */}
          <div className="space-y-6">
            {projects.map((_, index) => (
              <Project key={index} index={index} />
            ))}
          </div>

          {/* Submit All Projects Button */}
          <motion.button
            onClick={handleSubmitAll}
            className={`w-full px-6 py-3 rounded-xl shadow-lg font-semibold text-white transition-all duration-300 ${projects.some((project) => project.isLoading) || projects.length === 0 ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"} transform hover:scale-105`}
            disabled={projects.some((project) => project.isLoading) || projects.length === 0}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            data-testid="submitAll"
          >
            {projects.some((project) => project.isLoading) ? "Analyzing Projects..." : "Upload and Analyze All Projects"}
          </motion.button>
        </div>
      </main>

      <Footer />
    </div>
  );
}
