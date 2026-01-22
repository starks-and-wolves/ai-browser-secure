'use client'

import { useState } from 'react'

interface CodeBlockProps {
	code: string | object
	language?: string
	title?: string
	maxHeight?: string
}

export default function CodeBlock({ code, language = 'json', title, maxHeight = '400px' }: CodeBlockProps) {
	const [copied, setCopied] = useState(false)

	// Convert object to formatted JSON string if needed
	const codeString = typeof code === 'string' ? code : JSON.stringify(code, null, 2)

	const handleCopy = async () => {
		try {
			await navigator.clipboard.writeText(codeString)
			setCopied(true)
			setTimeout(() => setCopied(false), 2000)
		} catch (err) {
			console.error('Failed to copy:', err)
		}
	}

	return (
		<div className="bg-gray-900 rounded-lg overflow-hidden border border-gray-700">
			{/* Header */}
			<div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
				<div className="flex items-center gap-2">
					{title && <span className="text-sm font-semibold text-white">{title}</span>}
					<span className="text-xs text-gray-400">{language}</span>
				</div>
				<button
					onClick={handleCopy}
					className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
				>
					{copied ? '✓ Copied!' : 'Copy'}
				</button>
			</div>

			{/* Code Content */}
			<div
				className="overflow-auto p-4"
				style={{ maxHeight }}
			>
				<pre className="text-sm">
					<code className="text-gray-300 font-mono">{codeString}</code>
				</pre>
			</div>
		</div>
	)
}
