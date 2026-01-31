import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8010',
});

export const searchProcess = async (number) => {
    const response = await api.get(`/processes/${number}`);
    return response.data;
};

export default api;
