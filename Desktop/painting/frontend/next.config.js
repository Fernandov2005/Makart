/** @type {import('next').NextConfig} */
const nextConfig = {
  // External packages configuration
  serverExternalPackages: [],
  
  // Image optimization settings
  images: {
    domains: [],
    unoptimized: false,
  },
  
  // Performance optimizations
  reactStrictMode: true,
  
  // Handle large files in production
  webpack: (config) => {
    config.externals = [...(config.externals || [])];
    return config;
  },
}

module.exports = nextConfig 