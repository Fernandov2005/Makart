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
      <div className="min-h-screen">
        {/* Header */}
        <header className="glass sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <Image 
                    src="/logo-handshake.png" 
                    alt="Makart Logo" 
                    width={64} 
                    height={64} 
                    className="rounded-full shadow-2xl ring-4 ring-white/50" 
                  />
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-400 rounded-full border-3 border-white shadow-lg"></div>
                </div>
                <div>
                  <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
                    Makart Studio
                  </h1>
                  <p className="text-lg text-gray-600 font-medium">✨ Particle Animation Platform</p>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <p className="text-sm text-gray-600 font-medium">Welcome back,</p>
                  <p className="text-lg font-bold text-gray-900">{user?.email}</p>
                </div>
                <button
                  onClick={logout}
                  className="px-6 py-3 text-sm font-semibold text-gray-700 glass-card rounded-xl hover:scale-105 transition-all duration-300 shadow-lg"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-16 slide-up">
            <h2 className="text-6xl font-bold text-gray-900 mb-8 tracking-tight leading-tight">
              Transform Your Art Into{' '}
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent">
                Magic
              </span>
            </h2>
            <p className="text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed font-medium">
              Upload your paintings and watch them come alive with stunning particle animations. 
              Create professional-quality animated artworks in seconds.
            </p>
          </div>

          {/* Upload Area */}
          <div className="glass-card rounded-3xl p-10 mb-10 fade-in">
            <div
              className={`border-2 border-dashed rounded-3xl p-20 text-center transition-all duration-500 cursor-pointer ${
                dragOver 
                  ? 'border-blue-400 bg-blue-50/30 scale-[1.02] shadow-2xl' 
                  : file 
                  ? 'border-green-400 bg-green-50/30 shadow-xl' 
                  : 'border-gray-300 hover:border-blue-300 hover:bg-blue-50/20 hover:scale-[1.01] hover:shadow-xl'
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
                <div className="space-y-8">
                  <div className="w-28 h-28 mx-auto bg-gradient-to-br from-green-100 to-green-200 rounded-3xl flex items-center justify-center shadow-2xl">
                    <span className="text-4xl">✅</span>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900 mb-2">{file.name}</p>
                    <p className="text-xl text-gray-600 mb-4">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    <button
                      onClick={(e) => { e.stopPropagation(); resetUpload(); }}
                      className="glass-button px-6 py-3 text-white font-semibold rounded-xl transition-all duration-300"
                    >
                      Choose different file
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-8">
                  <div className="w-28 h-28 mx-auto bg-gradient-to-br from-blue-100 to-purple-100 rounded-3xl flex items-center justify-center shadow-2xl">
                    <span className="text-4xl">🎨</span>
                  </div>
                  <div>
                    <p className="text-3xl font-bold text-gray-900 mb-3">Drop your art 🎨</p>
                    <p className="text-xl text-gray-600 mb-2">or click to browse files</p>
                    <p className="text-lg text-gray-500">PNG, JPG, JPEG up to 50MB</p>
                  </div>
                </div>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="mt-8 glass-card rounded-2xl p-6 border-red-200 bg-red-50/70">
                <div className="flex items-start">
                  <span className="text-red-400 text-2xl mr-4">⚠️</span>
                  <p className="text-red-700 font-semibold text-lg">{error}</p>
                </div>
              </div>
            )}

            {/* Customization Options */}
            {file && !error && (
              <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="space-y-4">
                  <label className="block text-lg font-bold text-gray-700 tracking-wide">
                    ⏱️ Duration
                  </label>
                  <select
                    value={options.duration}
                    onChange={(e) => setOptions({...options, duration: parseInt(e.target.value)})}
                    className="glass-input w-full px-5 py-4 rounded-xl text-gray-900 font-semibold text-lg"
                  >
                    <option value={5}>5 seconds</option>
                    <option value={10}>10 seconds</option>
                    <option value={15}>15 seconds</option>
                    <option value={30}>30 seconds</option>
                  </select>
                </div>

                <div className="space-y-4">
                  <label className="block text-lg font-bold text-gray-700 tracking-wide">
                    💎 Quality
                  </label>
                  <select
                    value={options.quality}
                    onChange={(e) => setOptions({...options, quality: e.target.value})}
                    className="glass-input w-full px-5 py-4 rounded-xl text-gray-900 font-semibold text-lg"
                  >
                    <option value="standard">Standard</option>
                    <option value="high">High</option>
                    <option value="ultra">Ultra</option>
                  </select>
                </div>

                <div className="space-y-4">
                  <label className="block text-lg font-bold text-gray-700 tracking-wide">
                    🎭 Animation Style
                  </label>
                  <select
                    value={options.style}
                    onChange={(e) => setOptions({...options, style: e.target.value})}
                    className="glass-input w-full px-5 py-4 rounded-xl text-gray-900 font-semibold text-lg"
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
              <div className="mt-12 text-center">
                <button
                  onClick={handleSubmit}
                  disabled={isProcessing}
                  className="glass-button px-16 py-6 text-white font-bold text-xl rounded-3xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-2xl"
                >
                  {isProcessing ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-4 h-7 w-7 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating Magic...
                    </>
                  ) : (
                    '✨ Create Animation'
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Progress & Status */}
          {(isProcessing || status) && (
            <div className="glass-card rounded-3xl p-10 mb-10 fade-in">
              <div className="text-center">
                <h3 className="text-3xl font-bold text-gray-900 mb-8">
                  {status}
                </h3>
                {isProcessing && (
                  <div className="w-full bg-white/50 rounded-full h-6 mb-8 shadow-inner backdrop-blur-sm">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-6 rounded-full transition-all duration-1000 shadow-lg"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                )}
                <p className="text-xl text-gray-600 font-medium">
                  {isProcessing ? 'Please wait while we process your artwork...' : ''}
                </p>
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="glass-card rounded-3xl p-10 fade-in">
              <div className="text-center">
                <div className="w-24 h-24 mx-auto bg-gradient-to-br from-green-100 to-green-200 rounded-3xl flex items-center justify-center mb-8 shadow-2xl">
                  <span className="text-5xl">🎉</span>
                </div>
                <h3 className="text-4xl font-bold text-gray-900 mb-8">
                  {result.message}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-10 text-lg">
                  <div className="glass-card rounded-2xl p-6 shadow-lg">
                    <p className="font-bold text-gray-900 mb-2">📁 File</p>
                    <p className="text-gray-600 font-medium">{result.filename}</p>
                  </div>
                  <div className="glass-card rounded-2xl p-6 shadow-lg">
                    <p className="font-bold text-gray-900 mb-2">⏱️ Duration</p>
                    <p className="text-gray-600 font-medium">{result.duration}s</p>
                  </div>
                  <div className="glass-card rounded-2xl p-6 shadow-lg">
                    <p className="font-bold text-gray-900 mb-2">💎 Quality</p>
                    <p className="text-gray-600 font-medium">{result.quality}</p>
                  </div>
                  <div className="glass-card rounded-2xl p-6 shadow-lg">
                    <p className="font-bold text-gray-900 mb-2">🎭 Style</p>
                    <p className="text-gray-600 font-medium">{result.style}</p>
                  </div>
                </div>
                <button
                  onClick={resetUpload}
                  className="mt-10 glass-button px-12 py-5 text-white font-bold text-xl rounded-2xl transition-all duration-300 shadow-2xl"
                >
                  ✨ Create Another Animation
                </button>
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="text-center py-8 mt-16">
          <p className="text-gray-500 font-medium opacity-70">
            © 2024 Makart Studio - Bringing Art to Life
          </p>
        </footer>
      </div>
    </ProtectedRoute>
  );
}
