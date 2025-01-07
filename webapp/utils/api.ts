import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

interface Smell {
    smell_name: string;
    function_name: string;  
    line: number;  
    description: string;  
    additional_info: string;  
}

interface DetectResponse {
    smells: Smell[];
    message?: string;
    result?: string;
}

interface GenerateReportResponse {
    report_data: Record<string, any>;
}

// Helper function for consistent error handling
function handleErrorResponse(error: any, fallbackData: any = {}) {
    console.error("API Error:", error.response?.data || error.message || error);
    return fallbackData;
}

// AI-based code smell detection
export async function detectAi(codeSnippet: string): Promise<DetectResponse> {
    try {
        const response = await axios.post(`${API_URL}/detect_smell_ai`, {
            code_snippet: codeSnippet,
        });

        return {
                smells: Array.isArray(response.data.smells) ? response.data.smells : [],
                message: response.data.message || "No message available",
                result: response.data.result || "No results available",
            };
    } catch (error) {
        return handleErrorResponse(error, {
            smells: [],
            message: "Error detecting AI-based code smells.",
            result: null,
        });
    }
}

// Static analysis-based code smell detection
export async function detectStatic(codeSnippet: string): Promise<DetectResponse> {
    try {
        const response = await axios.post(`${API_URL}/detect_smell_static`, {
            code_snippet: codeSnippet,
        });

        return {
                smells: Array.isArray(response.data.smells) ? response.data.smells : [],
                message: response.data.message || "No message available",
                result: response.data.result || "No results available",
            };
            
    } catch (error) {
        return handleErrorResponse(error, { smells: [] });
    }
}


// Generate project report
export async function generateReport(projects: any[]): Promise<GenerateReportResponse> {
    try {
        const response = await axios.post(`${API_URL}/generate_report`, { projects });
        return response.data;
    } catch (error) {
        return handleErrorResponse(error, { report_data: {} });
    }
}
