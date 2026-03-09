import axios from 'axios';

// API configuration from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000;

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: parseInt(API_TIMEOUT),
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for logging (development only)
if (import.meta.env.VITE_DEBUG === 'true') {
    api.interceptors.request.use(
        (config) => {
            console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
            return config;
        },
        (error) => {
            console.error('[API Request Error]', error);
            return Promise.reject(error);
        }
    );
}

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Server responded with error status
            console.error(`[API Error] ${error.response.status}:`, error.response.data);
        } else if (error.request) {
            // Request made but no response received
            console.error('[API Error] No response from server');
        } else {
            // Error in request setup
            console.error('[API Error]', error.message);
        }
        return Promise.reject(error);
    }
);

export const searchProcess = async (number) => {
    const response = await api.get(`/processes/${number}`);
    return response.data;
};

export const getProcessInstance = async (number, index) => {
    const response = await api.get(`/processes/${number}/instances/${index}`);
    return response.data;
};

export const getProcessInstances = async (number) => {
    const response = await api.get(`/processes/${number}/instances`);
    return response.data;
};

export const bulkSearch = async (numbers) => {
    const response = await api.post('/processes/bulk', { numbers });
    return response.data;
};

export const bulkSubmit = async (numbers) => {
    const response = await api.post('/processes/bulk/submit', { numbers });
    return response.data; // { job_id, status, total, ... }
};

export const getBulkJob = async (jobId, page = 1, perPage = 50) => {
    const response = await api.get(`/processes/bulk/${jobId}`, {
        params: { page, per_page: perPage },
        timeout: 60000, // 60s timeout for large bulk jobs
    });
    return response.data;
};

export const getStats = async () => {
    const response = await api.get('/stats');
    return response.data;
};

export const testSQLConnection = async (config) => {
    const response = await api.post('/sql/test', config);
    return response.data;
};

export const importFromSQL = async (config) => {
    const response = await api.post('/sql/import', config);
    return response.data;
};

export const getHistory = async () => {
    const response = await api.get('/history');
    return response.data;
};

export const clearHistory = async () => {
    const response = await api.delete('/history');
    return response.data;
};

export const getMetrics = async (hours = 24) => {
    const response = await api.get('/metrics', {
        params: { hours }
    });
    return response.data;
};

export const getAlerts = async (limit = 20) => {
    const response = await api.get('/metrics/alerts', {
        params: { limit }
    });
    return response.data;
};

export const testFusionConnection = async (numeroCnj) => {
    const response = await api.get('/fusion/test', {
        params: { numero_cnj: numeroCnj }
    });
    return response.data;
};

export const getFusionStatus = async () => {
    const response = await api.get('/fusion/status');
    return response.data;
};

export const updateFusionCookie = async (cookie) => {
    const response = await api.patch('/fusion/cookie', { cookie });
    return response.data;
};

export default api;
