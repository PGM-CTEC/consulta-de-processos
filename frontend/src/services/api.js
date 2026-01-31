import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
});

export const searchProcess = async (number) => {
    const response = await api.get(`/processes/${number}`);
    return response.data;
};

export default api;
