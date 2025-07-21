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

export const register = async (email: string, password: string) => {
  const response = await fetchApi('/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  return response.json();
};

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

export const getCurrentUser = async () => {
  const response = await fetchApi('/user');
  return response.json();
};

interface UploadOptions {
  duration: number;
  quality: string;
  style: string;
}

export const uploadFile = async (file: File, options: UploadOptions, onUploadProgress: (progress: number) => void) => {
  // Log file details for debugging
  console.log('Uploading file:', {
    name: file.name,
    size: file.size,
    sizeInMB: (file.size / 1024 / 1024).toFixed(2),
    type: file.type
  });

  // Validate file size (50MB limit)
  const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
  if (file.size > MAX_FILE_SIZE) {
    throw new Error(`File too large. Maximum size is 50MB, but your file is ${(file.size / 1024 / 1024).toFixed(2)}MB.`);
  }

  // Validate file type
  if (!file.type.startsWith('image/')) {
    throw new Error('Please upload an image file (PNG, JPG, JPEG, GIF, BMP, WebP, etc.)');
  }

  // Create form data with file and options
  const formData = new FormData();
  formData.append('file', file);
  formData.append('duration', String(options.duration));
  formData.append('quality', options.quality);
  formData.append('style', options.style);

  // Progress tracking with realistic updates
  let progress = 0;
  onUploadProgress(5); // Initial progress

  // Simulate upload progress (since we can't track actual upload progress easily)
  const progressInterval = setInterval(() => {
    progress = Math.min(progress + Math.random() * 15 + 5, 85); // Increment by 5-20%
    onUploadProgress(Math.round(progress));
  }, 800);

  try {
    // Create AbortController for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, 300000); // 5 minutes timeout for large files

    console.log('Starting upload to /api/upload...');

    // Upload file with processing
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
      credentials: 'include',
      signal: controller.signal,
    });
    
    // Clear timeout and progress interval
    clearTimeout(timeoutId);
    clearInterval(progressInterval);
    onUploadProgress(100);
    
    if (!response.ok) {
      console.error('Upload failed:', {
        status: response.status,
        statusText: response.statusText
      });
      
      let errorMessage = 'Upload failed. Please try again.';
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
        console.error('Error details:', errorData);
      } catch (parseError) {
        console.error('Could not parse error response:', parseError);
      }
      
      throw new Error(errorMessage);
    }
    
    const result = await response.json();
    console.log('Upload successful:', result);
    
    return {
      success: result.success,
      message: result.message,
      filename: result.filename,
      duration: result.duration,
      quality: result.quality,
      style: result.style,
      processingTime: result.processingTime,
      fileSize: result.fileSize,
      downloadUrl: result.downloadUrl,
      particleCount: result.particleCount,
      details: result.details
    };
    
  } catch (error) {
    // Clean up progress tracking
    clearInterval(progressInterval);
    onUploadProgress(0);
    
    console.error('Upload error:', error);
    
    // Handle specific error types
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Upload timed out. Please try again with a smaller file or better internet connection.');
      }
      throw error;
    }
    
    throw new Error('Upload failed. Please try again.');
  }
}; 