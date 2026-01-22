import type { NextConfig } from "next";

const nextConfig: NextConfig = {
        typescript: {
                ignoreBuildErrors: true,
        },
        eslint: {
                ignoreDuringBuilds: true,
        },
        allowedDevOrigins: ["*.replit.dev", "*.repl.co", "*.replit.app"],
};

export default nextConfig;