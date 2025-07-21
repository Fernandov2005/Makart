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
  const [bypassValidation, setBypassValidation] = useState(true); // Added bypass toggle
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (selectedFile: File) => {
    // Always log the file info for debugging
    console.log('File details:', {
      name: selectedFile.name,
      size: selectedFile.size,
      sizeInMB: (selectedFile.size / 1024 / 1024).toFixed(2),
      type: selectedFile.type
    });
    
    // BYPASS: If bypass is enabled, accept files under 50MB
    if (bypassValidation && selectedFile.size <= 50 * 1024 * 1024) {
      console.log('🔓 Validation bypassed - file accepted');
      setError('');
      return true;
    }

    // Normal validation flow
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please upload an image file (PNG, JPG, JPEG, etc.)');
      return false;
    }

    const maxSize = 25 * 1024 * 1024; // 25MB in bytes
    if (selectedFile.size > maxSize) {
      setError(`File too large. Your file is ${(selectedFile.size / 1024 / 1024).toFixed(2)}MB but we support up to 25MB.`);
      return false;
    }

    if (selectedFile.size < 1024) { // Less than 1KB
      setError('File appears to be empty or corrupted.');
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
    setStatus('Creating your masterpiece...');
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
      
      // Log the actual error for debugging
      console.log('File size:', file?.size, 'bytes (', (file?.size || 0) / 1024 / 1024, 'MB)');
      console.log('Error message:', errorMessage);
      
      // Use the original error message which contains more details
      setError(errorMessage || 'Something went wrong. Please try again.');
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
        {/* Sticky Glass Navbar */}
        <header className="glass-navbar sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Image 
                    src="/logo-handshake.png" 
                    alt="Makart Logo" 
                    width={50} 
                    height={50} 
                    className="rounded-full shadow-lg" 
                  />
                  <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white shadow-md"></div>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
                    Makart Studio
                  </h1>
                  <p className="text-sm text-gray-600 font-medium">Particle Animation Platform</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right hidden sm:block">
                  <p className="text-sm text-gray-600 font-medium">Welcome back,</p>
                  <p className="font-semibold text-gray-900">{user?.email}</p>
                </div>
                <button
                  onClick={logout}
                  className="glass-button px-4 py-2 text-sm font-semibold hover:scale-105"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-4xl mx-auto px-6 py-12">
          <div className="text-center mb-12 slide-up">
            <h2 className="text-5xl font-bold text-gray-900 mb-6 tracking-tight leading-tight">
              Transform Your Art Into{' '}
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent">
                Magic
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed font-medium">
              Upload your paintings and watch them come alive with stunning particle animations.
            </p>
          </div>

          {/* Upload Area */}
          <div className="glass-container p-8 mb-8 fade-in">
            <div
              className={`border-2 border-dashed rounded-3xl p-16 text-center transition-all duration-500 cursor-pointer ${
                dragOver 
                  ? 'drag-glow scale-[1.02]' 
                  : file 
                  ? 'border-green-400 bg-green-50/20' 
                  : 'border-gray-300 hover:border-blue-300 hover:bg-blue-50/10 hover:scale-[1.01]'
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
                  <div className="w-20 h-20 mx-auto bg-gradient-to-br from-green-100 to-green-200 rounded-full flex items-center justify-center shadow-xl">
                    <span className="text-3xl">✅</span>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-gray-900 mb-1">{file.name}</p>
                    <p className="text-lg text-gray-600 mb-4">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    <button
                      onClick={(e) => { e.stopPropagation(); resetUpload(); }}
                      className="glass-button px-4 py-2 text-sm font-semibold"
                    >
                      Choose different file
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="w-24 h-24 mx-auto bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center shadow-xl">
                    <span className="text-4xl">🖼️</span>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900 mb-2">Drop your art here</p>
                    <p className="text-lg text-gray-600 mb-1">or click to browse files</p>
                    <p className="text-sm text-gray-500">PNG, JPG, JPEG - any size</p>
                  </div>
                </div>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="mt-6 glass-container p-5 border border-red-300/30 bg-red-50/20 animate-pulse">
                <div className="flex items-start">
                  <span className="text-red-500 text-2xl mr-4">⚠️</span>
                  <div>
                    <p className="text-red-600 font-semibold text-lg">{error}</p>
                    <div className="mt-3 flex gap-3">
                      <button 
                        onClick={() => setBypassValidation(!bypassValidation)}
                        className="text-blue-600 underline text-sm hover:text-blue-700 font-medium"
                      >
                        {bypassValidation ? '✓ Bypass Enabled' : '○ Enable Bypass'}
                      </button>
                      <button 
                        onClick={resetUpload}
                        className="text-blue-600 underline text-sm hover:text-blue-700 font-medium"
                      >
                        Try Again
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Customization Options */}
            {file && !error && (
              <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-3">
                  <label className="block text-sm font-bold text-gray-800 tracking-wide">
                    Duration
                  </label>
                  <select
                    value={options.duration}
                    onChange={(e) => setOptions({...options, duration: parseInt(e.target.value)})}
                    className="glass-input w-full px-4 py-3 text-gray-900 font-semibold"
                  >
                    <option value={5}>5 seconds</option>
                    <option value={10}>10 seconds</option>
                    <option value={15}>15 seconds</option>
                    <option value={30}>30 seconds</option>
                  </select>
                </div>

                <div className="space-y-3">
                  <label className="block text-sm font-bold text-gray-800 tracking-wide">
                    Quality
                  </label>
                  <select
                    value={options.quality}
                    onChange={(e) => setOptions({...options, quality: e.target.value})}
                    className="glass-input w-full px-4 py-3 text-gray-900 font-semibold"
                  >
                    <option value="standard">Standard</option>
                    <option value="high">High</option>
                    <option value="ultra">Ultra</option>
                  </select>
                </div>

                <div className="space-y-3">
                  <label className="block text-sm font-bold text-gray-800 tracking-wide">
                    Animation Style
                  </label>
                  <select
                    value={options.style}
                    onChange={(e) => setOptions({...options, style: e.target.value})}
                    className="glass-input w-full px-4 py-3 text-gray-900 font-semibold"
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
              <div className="mt-8 text-center">
                <button
                  onClick={handleSubmit}
                  disabled={isProcessing}
                  className="glass-button px-12 py-4 text-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isProcessing ? (
                    <>
                      <div className="spinner inline-block mr-3" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
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
            <div className="glass-container p-8 mb-8 scale-in">
              <div className="text-center">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">
                  {status}
                </h3>
                {isProcessing && (
                  <div className="w-full bg-white/30 rounded-full h-3 mb-6 shadow-inner">
                    <div 
                      className="progress-gradient h-3 rounded-full transition-all duration-1000"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                )}
                <p className="text-lg text-gray-600 font-medium">
                  {isProcessing ? 'Please wait while we process your artwork...' : ''}
                </p>
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="glass-container p-8 scale-in">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto bg-gradient-to-br from-green-100 to-green-200 rounded-full flex items-center justify-center mb-6 shadow-xl">
                  <span className="text-3xl">🎉</span>
                </div>
                <h3 className="text-3xl font-bold text-gray-900 mb-6">
                  {result.message}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                  <div className="glass-container p-4 text-center">
                    <p className="font-bold text-gray-900 mb-1 text-sm">File</p>
                    <p className="text-gray-600 font-medium text-xs">{result.filename}</p>
                  </div>
                  <div className="glass-container p-4 text-center">
                    <p className="font-bold text-gray-900 mb-1 text-sm">Duration</p>
                    <p className="text-gray-600 font-medium text-xs">{result.duration}s</p>
                  </div>
                  <div className="glass-container p-4 text-center">
                    <p className="font-bold text-gray-900 mb-1 text-sm">Quality</p>
                    <p className="text-gray-600 font-medium text-xs">{result.quality}</p>
                  </div>
                  <div className="glass-container p-4 text-center">
                    <p className="font-bold text-gray-900 mb-1 text-sm">Style</p>
                    <p className="text-gray-600 font-medium text-xs">{result.style}</p>
                  </div>
                </div>
                <button
                  onClick={resetUpload}
                  className="mt-8 glass-button px-8 py-3 text-lg font-bold"
                >
                  ✨ Create Another Animation
                </button>
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="text-center py-6 mt-12">
          <p className="text-sm text-gray-500 font-medium opacity-50">
            © 2024 Makart Studio - Bringing Art to Life
          </p>
        </footer>
      </div>
    </ProtectedRoute>
  );
}
