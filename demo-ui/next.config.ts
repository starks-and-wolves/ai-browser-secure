import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
        typescript: {
                ignoreBuildErrors: true,
        },
        eslint: {
                ignoreDuringBuilds: true,
        },
        env: {
                NEXT_PUBLIC_API_URL: '',
        },
        allowedDevOrigins: [
                '*.replit.dev',
                '*.repl.co',
                '*.replit.app',
                '4cd06627-c45d-4b3a-8636-efcc5fd7aea5-00-1rr20l9ziz5f8.sisko.replit.dev',
        ],
        async rewrites() {
                return [
                        {
                                source: '/api/:path*',
                                destination: 'http://localhost:8000/api/:path*',
                        },
                ]
        },
}

export default nextConfig