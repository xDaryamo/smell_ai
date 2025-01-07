"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

type ContextSmell = {
  function_name: string;
  line: number;
  smell_name: string;
  description: string;
  additional_info: string;
};

export type ProjectType = {
  name: string;
  files: File[] | null;
  data: {
    files: string[] | null;
    message: string;
    result: string | null;
    smells: ContextSmell[] | null;
  };
  isLoading: boolean;
};

type ProjectContextType = {
  projects: ProjectType[];
  addProject: () => void;
  updateProject: (index: number, project: Partial<ProjectType>) => void;
  removeProject: (index: number) => void;
};

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const useProjectContext = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error("useProjectContext must be used within a ProjectProvider");
  }
  return context;
};

export const ProjectProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [projects, setProjects] = useState<ProjectType[]>([]);

  const addProject = () => {
    setProjects((prevProjects) => [
      ...prevProjects,
      { 
        name: "",
        files: null,
        data: { files: null, message: "", result: null, smells: null },
        isLoading: false 
      },
    ]);
  };

  const updateProject = (index: number, project: Partial<ProjectType>) => {
    setProjects((prevProjects) => {
      const updatedProjects = [...prevProjects];
      updatedProjects[index] = { ...updatedProjects[index], ...project };
      return updatedProjects;
    });
  };

  const removeProject = (index: number) => {
    setProjects((prevProjects) => prevProjects.filter((_, i) => i !== index));
  };

  return (
    <ProjectContext.Provider value={{ projects, addProject, updateProject, removeProject }}>
      {children}
    </ProjectContext.Provider>
  );
};
