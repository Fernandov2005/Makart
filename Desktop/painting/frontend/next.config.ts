import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ['formidable'],
  // Increase body size limits for file uploads
  serverRuntimeConfig: {
    maxFileSize: '50mb',
  },
  // Enable image optimization
  images: {
    formats: ['image/webp', 'image/avif'],
  },
};

export default nextConfig;
