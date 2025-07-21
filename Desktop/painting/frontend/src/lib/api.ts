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
    let errorMessage = 'API request failed';
    
    try {
      const errorData = await response.json();
      errorMessage = errorData.error || errorMessage;
    } catch {
      // If we can't parse the error response, use status-based messages
      if (response.status === 413) {
        errorMessage = 'File too large. Please choose a smaller image (max 50MB).';
      } else if (response.status === 500) {
        errorMessage = 'Server error. Please try again.';
      } else if (response.status === 401) {
        errorMessage = 'Authentication required. Please log in again.';
      }
    }
    
    throw new Error(errorMessage);
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
  
  try {
    const response = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });
    
    onUploadProgress(100);
    
    if (!response.ok) {
      let errorMessage = 'Upload failed';
      
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch {
        // If we can't parse the error response, use status-based messages
        if (response.status === 413) {
          errorMessage = 'File too large. Please choose a smaller image (max 50MB).';
        } else if (response.status === 500) {
          errorMessage = 'Server error during upload. Please try again.';
        } else if (response.status === 401) {
          errorMessage = 'Authentication required. Please log in again.';
        }
      }
      
      throw new Error(errorMessage);
    }
    
    // Parse the JSON response
    const result = await response.json();
    return result;
  } catch (error) {
    onUploadProgress(0); // Reset progress on error
    throw error;
  }
}; 