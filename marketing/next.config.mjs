/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  // Static, server-rendered HTML is fully crawlable by search engines and AI
  // answer engines (no client-side JS required to read the content).
  trailingSlash: false,
};

export default nextConfig;
