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
}

export default nextConfig
