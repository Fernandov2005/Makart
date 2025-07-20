// src/lib/api.ts
import axios, { AxiosProgressEvent } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://makart.onrender.com/api';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

export const login = async (email: string, password: string) => {
  return api.post('/login', { email, password });
};

export const logout = async () => {
  return api.post('/logout');
};

export const checkSession = async () => {
  return api.get('/session');
};

interface UploadOptions {
  duration: number;
  quality: string;
  style: string;
}

export const uploadFile = async (file: File, options: UploadOptions, onUploadProgress: (progress: number) => void) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('duration', String(options.duration));
  formData.append('quality', options.quality);
  formData.append('style', options.style);

  return api.post('/upload', formData, {
    responseType: 'blob',
    onUploadProgress: (progressEvent: AxiosProgressEvent) => {
      if (progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onUploadProgress(percentCompleted);
      }
    },
  });
};

export default api; 