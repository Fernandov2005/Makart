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
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center glass-card rounded-3xl p-12 fade-in">
          <Image src="/logo-handshake.png" alt="Makart Logo" width={80} height={80} className="mx-auto mb-8 rounded-full shadow-2xl" />
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-6"></div>
          <p className="text-gray-600 text-lg font-medium">Loading Makart Studio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md slide-up">
        {/* Logo and Branding */}
        <div className="text-center mb-12">
          <div className="relative mb-8">
            <Image 
              src="/logo-handshake.png" 
              alt="Makart Logo" 
              width={120} 
              height={120} 
              className="mx-auto rounded-full shadow-2xl ring-4 ring-white/50" 
            />
            <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-green-400 rounded-full border-4 border-white shadow-lg"></div>
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-3 tracking-tight">
            Makart Studio
          </h1>
          <p className="text-xl text-gray-600 font-medium">
            ✨ Particle Animation Platform
          </p>
        </div>

        {/* Login Form */}
        <div className="glass-card rounded-3xl p-10 mb-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-3 tracking-tight">
              Welcome Back
            </h2>
            <p className="text-gray-600 text-lg">
              Sign in to transform your art into magic 🎨
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-5">
              {/* Email Input */}
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-3 tracking-wide">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="text-gray-400 text-xl">📧</span>
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    disabled={isSubmitting}
                    className="glass-input w-full pl-12 pr-4 py-4 text-gray-900 rounded-2xl placeholder-gray-400 font-medium text-lg disabled:opacity-50"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>
              
              {/* Password Input */}
              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-3 tracking-wide">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="text-gray-400 text-xl">🔒</span>
                  </div>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    disabled={isSubmitting}
                    className="glass-input w-full pl-12 pr-4 py-4 text-gray-900 rounded-2xl placeholder-gray-400 font-medium text-lg disabled:opacity-50"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>
            </div>
            
            {/* Error Display */}
            {error && (
              <div className="glass-card rounded-2xl p-4 border-red-200 bg-red-50/70">
                <div className="flex items-start">
                  <span className="text-red-400 text-xl mr-3 mt-1">⚠️</span>
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
              className="glass-button w-full px-6 py-5 text-white font-bold text-lg rounded-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isSubmitting ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing you in...
                </div>
              ) : (
                '✨ Sign In to Create Magic'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-500 font-medium">
              Transform your paintings into magical particle animations
            </p>
          </div>
        </div>

        {/* Additional Info */}
        <div className="text-center">
          <p className="text-sm text-gray-500 font-medium opacity-70">
            © 2024 Makart Studio - Bringing Art to Life
          </p>
        </div>
      </div>
    </div>
  );
} 