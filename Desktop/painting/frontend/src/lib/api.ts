// src/lib/api.ts
// Always use local Next.js API routes instead of external backend
const API_URL = '/api';

async function fetchApi(path: string, options: RequestInit = {}) {
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Set credentials to 'include' to send cookies
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

  // Simulate upload progress
  onUploadProgress(30);
  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });
  onUploadProgress(100);
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Upload failed');
  }
  
  // Parse the JSON response
  const result = await response.json();
  return result;
}; 