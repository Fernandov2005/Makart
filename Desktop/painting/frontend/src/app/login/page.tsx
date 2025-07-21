'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useState, FormEvent, useEffect } from 'react';
import Image from 'next/image';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login, isAuthenticated, error: authError, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    if (authError) {
      setError(authError);
    }
  }, [authError]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    setError('');
    
    try {
      await login(email, password);
      router.push('/');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="glass-container p-12 text-center scale-in">
          <Image 
            src="/logo-handshake.png" 
            alt="Makart Logo" 
            width={80} 
            height={80} 
            className="mx-auto mb-8 rounded-full shadow-2xl" 
          />
          <div className="spinner mx-auto mb-6"></div>
          <p className="text-gray-700 text-lg font-medium">Loading Makart Studio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md fade-in">
        {/* Logo and Branding */}
        <div className="text-center mb-8">
          <div className="relative mb-6">
            <Image 
              src="/logo-handshake.png" 
              alt="Makart Logo" 
              width={100} 
              height={100} 
              className="mx-auto rounded-full shadow-2xl" 
            />
            <div className="absolute -bottom-1 -right-1 w-7 h-7 bg-green-400 rounded-full border-3 border-white shadow-lg"></div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2 tracking-tight">
            Makart Studio
          </h1>
          <p className="text-lg text-gray-600 font-medium">
            Particle Animation Platform ✨
          </p>
        </div>

        {/* Login Form */}
        <div className="glass-container p-8 mb-6">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2 tracking-tight">
              Welcome Back
            </h2>
            <p className="text-gray-600 text-lg">
              Sign in to transform your art into magic
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-5">
              {/* Email Input */}
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-gray-800 mb-3 tracking-wide">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="text-gray-500 text-lg">✉️</span>
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    disabled={isSubmitting}
                    className="glass-input w-full pl-12 pr-4 py-4 text-lg disabled:opacity-50"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>
              
              {/* Password Input */}
              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-800 mb-3 tracking-wide">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="text-gray-500 text-lg">🔒</span>
                  </div>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    disabled={isSubmitting}
                    className="glass-input w-full pl-12 pr-4 py-4 text-lg disabled:opacity-50"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>
            </div>
            
            {/* Error Display */}
            {error && (
              <div className="glass-container p-4 border border-red-300/30 bg-red-50/20">
                <div className="flex items-start">
                  <span className="text-red-500 text-lg mr-3 mt-1">⚠️</span>
                  <div>
                    <p className="text-sm text-red-700 font-semibold">{error}</p>
                    {error.includes('Unable to connect') && (
                      <p className="text-xs text-red-600 mt-2">
                        The server may be starting up. Please wait a moment and try again.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="glass-button w-full px-6 py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isSubmitting ? (
                <div className="flex items-center justify-center">
                  <div className="spinner mr-3" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
                  Signing you in...
                </div>
              ) : (
                '✨ Sign In to Create Magic'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600 font-medium">
              Transform your paintings into magical particle animations
            </p>
          </div>
        </div>

        {/* Additional Info */}
        <div className="text-center">
          <p className="text-sm text-gray-500 font-medium opacity-50">
            © 2024 Makart Studio - Bringing Art to Life
          </p>
        </div>
      </div>
    </div>
  );
} 