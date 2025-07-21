'use client';

import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/contexts/AuthContext";
import { useState, useRef } from "react";
import { uploadFile } from "@/lib/api";
import Image from "next/image";

interface AnimationResult {
  success: boolean;
  filename: string;
  duration: string;
  quality: string;
  style: string;
  processingTime: string;
  fileSize: string;
  message: string;
  downloadUrl: string;
}

export default function Home() {
  const { user, logout } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [options, setOptions] = useState({ duration: 10, quality: 'ultra', style: 'particle_powder' });
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [result, setResult] = useState<AnimationResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (selectedFile: File) => {
    // Check file type
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please upload an image file (PNG, JPG, JPEG, etc.)');
      return false;
    }

    // Check file size (50MB limit)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (selectedFile.size > maxSize) {
      setError(`File too large. Maximum size is 50MB. Your file is ${(selectedFile.size / 1024 / 1024).toFixed(2)}MB.`);
      return false;
    }

    setError('');
    return true;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
        setResult(null);
        setStatus('');
      }
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && validateFile(droppedFile)) {
      setFile(droppedFile);
      setResult(null);
      setStatus('');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleSubmit = async () => {
    if (!file) return;
    
    setIsProcessing(true);
    setStatus('Uploading your masterpiece...');
    setProgress(0);
    setResult(null);
    setError('');
    
    try {
      const response = await uploadFile(file, options, setProgress);
      setStatus('Animation complete!');
      setResult(response);
    } catch (err: unknown) {
      console.error('Upload error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      if (errorMessage.includes('413') || errorMessage.includes('too large')) {
        setError('File too large. Please choose a smaller image (max 50MB).');
      } else {
        setError('Something went wrong. Please try again.');
      }
      setStatus('');
    } finally {
      setIsProcessing(false);
    }
  };

  const resetUpload = () => {
    setFile(null);
    setResult(null);
    setStatus('');
    setProgress(0);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white/90 backdrop-blur-xl border-b border-purple-100 sticky top-0 z-50 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Image 
                    src="/logo-handshake.png" 
                    alt="Makart Logo" 
                    width={60} 
                    height={60} 
                    className="rounded-full shadow-lg ring-2 ring-purple-100" 
                  />
                  <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-green-400 rounded-full border-2 border-white"></div>
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                    Makart Studio
                  </h1>
                  <p className="text-sm text-gray-600 font-medium">Particle Animation Platform</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm text-gray-600">Welcome back,</p>
                  <p className="font-semibold text-gray-900">{user?.email}</p>
                </div>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-12">
            <h2 className="text-5xl font-bold text-gray-900 mb-6">
              Transform Your Art Into{' '}
              <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Magic
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Upload your paintings and watch them come alive with stunning particle animations. 
              Create professional-quality animated artworks in seconds.
            </p>
          </div>

          {/* Upload Area */}
          <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl p-8 mb-8 border border-white/20">
            <div
              className={`border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 ${
                dragOver 
                  ? 'border-purple-400 bg-purple-50 scale-[1.02]' 
                  : file 
                  ? 'border-green-300 bg-green-50' 
                  : 'border-gray-300 hover:border-purple-300 hover:bg-purple-50/50 hover:scale-[1.01]'
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => !file && fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
              
              {file ? (
                <div className="space-y-6">
                  <div className="w-24 h-24 mx-auto bg-gradient-to-br from-green-100 to-green-200 rounded-full flex items-center justify-center shadow-lg">
                    <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-xl font-semibold text-gray-900">{file.name}</p>
                    <p className="text-lg text-gray-600">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    <button
                      onClick={(e) => { e.stopPropagation(); resetUpload(); }}
                      className="mt-3 text-purple-600 hover:text-purple-800 font-medium transition-colors"
                    >
                      Choose different file
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="w-24 h-24 mx-auto bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center shadow-lg">
                    <svg className="w-12 h-12 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-2xl font-semibold text-gray-900">Drop your artwork here</p>
                    <p className="text-lg text-gray-600">or click to browse files</p>
                    <p className="text-sm text-gray-500 mt-2">PNG, JPG, JPEG up to 50MB</p>
                  </div>
                </div>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-4">
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-red-600 font-medium">{error}</p>
                </div>
              </div>
            )}

            {/* Customization Options */}
            {file && !error && (
              <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="space-y-3">
                  <label className="block text-sm font-semibold text-gray-700">
                    Duration
                  </label>
                  <select
                    value={options.duration}
                    onChange={(e) => setOptions({...options, duration: parseInt(e.target.value)})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white shadow-sm text-gray-900 font-medium"
                  >
                    <option value={5}>5 seconds</option>
                    <option value={10}>10 seconds</option>
                    <option value={15}>15 seconds</option>
                    <option value={30}>30 seconds</option>
                  </select>
                </div>

                <div className="space-y-3">
                  <label className="block text-sm font-semibold text-gray-700">
                    Quality
                  </label>
                  <select
                    value={options.quality}
                    onChange={(e) => setOptions({...options, quality: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white shadow-sm text-gray-900 font-medium"
                  >
                    <option value="standard">Standard</option>
                    <option value="high">High</option>
                    <option value="ultra">Ultra</option>
                  </select>
                </div>

                <div className="space-y-3">
                  <label className="block text-sm font-semibold text-gray-700">
                    Animation Style
                  </label>
                  <select
                    value={options.style}
                    onChange={(e) => setOptions({...options, style: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white shadow-sm text-gray-900 font-medium"
                  >
                    <option value="particle_powder">✨ Particle Powder</option>
                    <option value="flowing_paint">🎨 Flowing Paint</option>
                    <option value="magical_dust">🪄 Magical Dust</option>
                    <option value="electric_sparks">⚡ Electric Sparks</option>
                    <option value="watercolor_bloom">🌸 Watercolor Bloom</option>
                  </select>
                </div>
              </div>
            )}

            {/* Action Button */}
            {file && !error && (
              <div className="mt-10 text-center">
                <button
                  onClick={handleSubmit}
                  disabled={isProcessing}
                  className="px-12 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold text-lg rounded-2xl hover:from-purple-700 hover:to-blue-700 transition-all transform hover:scale-105 hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-xl"
                >
                  {isProcessing ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating Magic...
                    </>
                  ) : (
                    '🎨 Create Animation'
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Progress & Status */}
          {(isProcessing || status) && (
            <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl p-8 mb-8 border border-white/20">
              <div className="text-center">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">
                  {status}
                </h3>
                {isProcessing && (
                  <div className="w-full bg-gray-200 rounded-full h-4 mb-6 shadow-inner">
                    <div 
                      className="bg-gradient-to-r from-purple-600 to-blue-600 h-4 rounded-full transition-all duration-500 shadow-sm"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                )}
                <p className="text-lg text-gray-600">
                  {isProcessing ? 'Please wait while we process your artwork...' : ''}
                </p>
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20">
              <div className="text-center">
                <div className="w-20 h-20 mx-auto bg-gradient-to-br from-green-100 to-green-200 rounded-full flex items-center justify-center mb-6 shadow-lg">
                  <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-3xl font-bold text-gray-900 mb-6">
                  {result.message}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-8 text-sm">
                  <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 shadow-sm">
                    <p className="font-semibold text-gray-900 mb-1">File</p>
                    <p className="text-gray-600">{result.filename}</p>
                  </div>
                  <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 shadow-sm">
                    <p className="font-semibold text-gray-900 mb-1">Duration</p>
                    <p className="text-gray-600">{result.duration}s</p>
                  </div>
                  <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 shadow-sm">
                    <p className="font-semibold text-gray-900 mb-1">Quality</p>
                    <p className="text-gray-600">{result.quality}</p>
                  </div>
                  <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 shadow-sm">
                    <p className="font-semibold text-gray-900 mb-1">Style</p>
                    <p className="text-gray-600">{result.style}</p>
                  </div>
                </div>
                <button
                  onClick={resetUpload}
                  className="mt-8 px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold text-lg rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all transform hover:scale-105 shadow-lg"
                >
                  ✨ Create Another Animation
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}
