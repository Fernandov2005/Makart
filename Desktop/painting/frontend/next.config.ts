import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ['formidable'],
  
  // Enable image optimization
  images: {
    formats: ['image/webp', 'image/avif'],
  },
};

export default nextConfig;
