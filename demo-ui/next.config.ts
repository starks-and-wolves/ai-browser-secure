import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
	/* config options here */
	typescript: {
		// Allow production builds even with type errors (for development)
		ignoreBuildErrors: false,
	},
	eslint: {
		// Allow production builds even with ESLint errors (for development)
		ignoreDuringBuilds: false,
	},
	// Allow Replit dev origins for /_next/* resources
	// This fixes the "Blocked cross-origin request" error on Replit
	experimental: {
		allowedDevOrigins: [
			'*.replit.dev',
			'*.repl.co',
		],
	},
}

export default nextConfig
