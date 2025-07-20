// src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://makart.onrender.com/api';

async function fetchApi(path: string, options: RequestInit = {}) {
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'omit', // Set credentials to 'omit' by default
  };
  const mergedOptions: RequestInit = {
    ...defaultOptions,
    ...options,
  };
  const requestUrl = `${API_URL}${path}`;
  const response = await fetch(requestUrl, mergedOptions);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'API request failed');
  }

  return response;
}

export const login = async (email: string, password: string) => {
  const response = await fetchApi('/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  return response.json();
};

export const logout = async () => {
  return fetchApi('/logout', { method: 'POST' });
};

export const checkSession = async () => {
  const response = await fetchApi('/session');
  return response.json();
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

  // Note: onUploadProgress is not directly supported by fetch.
  // A more advanced implementation would use XMLHttpRequest or a library like `axios-fetch-adapter`.
  // For now, we will simulate the progress.
  onUploadProgress(50); // Simulate 50% progress
  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData,
  });
  onUploadProgress(100); // Simulate 100% progress
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Upload failed');
  }
  
  return response.blob();
}; 