import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
	title: 'Browser-Use Demo | AI Browser Automation',
	description: '500x faster browser automation with AWI mode - Structured API vs DOM parsing comparison',
}

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode
}>) {
	return (
		<html lang="en">
			<body className="antialiased">{children}</body>
		</html>
	)
}
