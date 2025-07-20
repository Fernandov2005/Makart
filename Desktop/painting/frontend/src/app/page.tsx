'use client';

import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";
import { uploadFile } from "@/lib/api";

export default function Home() {
  const { user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [options, setOptions] = useState({ duration: 10, quality: 'ultra', style: 'particle_powder' });
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!file) return;
    setStatus('Uploading...');
    try {
      const response = await uploadFile(file, options, setProgress);
      setStatus('Processing...');
      // Handle the downloaded file
      const blob = new Blob([response.data], { type: 'video/mp4' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'animation.mp4';
      a.click();
      setStatus('Done!');
    } catch (error) {
      setStatus('Error!');
      console.error(error);
    }
  };

  return (
    <ProtectedRoute>
      <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-white">
        <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
          <h1 className="text-4xl font-bold text-center text-brand-purple">
            Welcome, {user?.email}
          </h1>
        </div>
        <div className="mt-8">
          <input type="file" onChange={handleFileChange} />
          <button onClick={handleSubmit} className="p-2 bg-brand-purple text-white rounded">
            Upload and Animate
          </button>
        </div>
        {status && (
          <div className="mt-4">
            <p>{status}</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-brand-purple h-2.5 rounded-full" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        )}
      </main>
    </ProtectedRoute>
  );
}
