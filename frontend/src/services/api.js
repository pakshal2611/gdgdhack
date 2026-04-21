import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

export async function uploadFile(file, onProgress) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    },
  });
  return response.data;
}

export async function getAnalysis(fileId) {
  const response = await api.get(`/analysis/${fileId}`);
  return response.data;
}

export async function sendChat(fileId, query) {
  const response = await api.post('/chat', { file_id: fileId, query });
  return response.data;
}

export async function downloadExcel(fileId) {
  const response = await api.get(`/export/${fileId}`, { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `financial_report_${fileId}.xlsx`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export async function getFiles() {
  const response = await api.get('/files');
  return response.data;
}

export default api;
