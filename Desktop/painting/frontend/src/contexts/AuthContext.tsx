'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { checkSession, login as apiLogin, logout as apiLogout } from '@/lib/api';

interface AuthContextType {
  isAuthenticated: boolean;
  user: { email: string } | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<{ email: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const verifySession = async () => {
      try {
        console.log('Checking session...');
        const data = await checkSession();
        console.log('Session response:', data);
        if (data.logged_in) {
          setIsAuthenticated(true);
          setUser({ email: data.email });
          console.log('Session valid, user authenticated');
        } else {
          console.log('No valid session found');
        }
      } catch (error) {
        console.error('Session check failed:', error);
        setError('Unable to connect to server');
      } finally {
        setLoading(false);
      }
    };
    verifySession();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      setLoading(true);
      console.log('Attempting login for:', email);
      
      const data = await apiLogin(email, password);
      console.log('Login response:', data);
      
      setIsAuthenticated(true);
      setUser({ email: data.email });
      setError(null);
      console.log('Login successful');
    } catch (error) {
      console.error('Login failed:', error);
      setError(error instanceof Error ? error.message : 'Login failed');
      setIsAuthenticated(false);
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiLogout();
      setIsAuthenticated(false);
      setUser(null);
      setError(null);
    } catch (error) {
      console.error('Logout failed:', error);
      // Still clear local state even if logout request fails
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 