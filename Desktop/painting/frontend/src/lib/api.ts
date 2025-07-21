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
      } else if (response.status === 408) {
        errorMessage = 'Upload timeout. Please try again or use a smaller file.';
      } else if (response.status === 0) {
        errorMessage = 'Network error. Please check your connection and try again.';
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
  const response = await fetchApi('/logout', {
    method: 'POST',
  });
  return response.json();
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
  // Conservative file validation before upload (25MB for testing)
  if (file.size > 25 * 1024 * 1024) {
    throw new Error(`File too large for processing. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB but we support up to 25MB. Try compressing your image or reducing its resolution.`);
  }

  console.log('Client-side upload validation passed for file size:', (file.size / 1024 / 1024).toFixed(2), 'MB');

  const formData = new FormData();
  formData.append('file', file);
  formData.append('duration', String(options.duration));
  formData.append('quality', options.quality);
  formData.append('style', options.style);

  // Enhanced progress simulation with more realistic stages
  const progressStages = [10, 25, 40, 60, 80, 95];
  let currentStage = 0;

  const progressInterval = setInterval(() => {
    if (currentStage < progressStages.length) {
      onUploadProgress(progressStages[currentStage]);
      currentStage++;
    }
  }, 800);

  try {
    // Create AbortController for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, 120000); // 2 minutes timeout

    const response = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
      signal: controller.signal,
      // Remove Content-Type header to let browser set it with boundary
      headers: {},
    });
    
    clearTimeout(timeoutId);
    clearInterval(progressInterval);
    onUploadProgress(100);
    
    if (!response.ok) {
      let errorMessage = 'Upload failed';
      
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
        
        // Add additional context from server response
        if (errorData.suggestion) {
          errorMessage += ` ${errorData.suggestion}`;
        }
      } catch {
        // Enhanced error handling based on status codes
        if (response.status === 413) {
          errorMessage = 'File too large for processing. Please use images under 15MB. Try compressing your image or reducing its resolution.';
        } else if (response.status === 500) {
          errorMessage = 'Server error during upload. Please try again.';
        } else if (response.status === 401) {
          errorMessage = 'Authentication required. Please log in again.';
        } else if (response.status === 415) {
          errorMessage = 'Unsupported file type. Please use PNG, JPG, or JPEG.';
        } else if (response.status === 408) {
          errorMessage = 'Upload timeout. Please try again or use a smaller file.';
        } else if (response.status === 0) {
          errorMessage = 'Network error. Please check your connection.';
        } else {
          errorMessage = `Upload failed (Error ${response.status}). Please try again with a smaller image file.`;
        }
      }
      
      throw new Error(errorMessage);
    }
    
    // Parse the JSON response
    const result = await response.json();
    return result;
  } catch (error) {
    clearInterval(progressInterval);
    onUploadProgress(0); // Reset progress on error
    
    // Handle different error types
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Upload timeout. Please try again or use a smaller file.');
      } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
        throw new Error('Network error. Please check your connection and try again.');
      }
      throw error;
    }
    
    throw new Error('Upload failed. Please try again with a smaller image file.');
  }
}; 