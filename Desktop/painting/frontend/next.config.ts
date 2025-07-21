import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ['formidable'],
  
  // Enable image optimization
  images: {
    formats: ['image/webp', 'image/avif'],
  },
  
  // Enable experimental features for better file upload handling
  experimental: {
    serverComponentsExternalPackages: ['formidable'],
  },
};

export default nextConfig;
