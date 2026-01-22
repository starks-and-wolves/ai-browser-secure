'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import TrajectoryPlayer from '@/components/showcase/TrajectoryPlayer'
import MetricsVisualization from '@/components/showcase/MetricsVisualization'
import CodeBlock from '@/components/shared/CodeBlock'
import { TrajectoryPlayerSkeleton, DemoSelectorSkeleton, ChartSkeleton, CodeBlockSkeleton } from '@/components/shared/LoadingSkeletons'
import { loadDemoManifest, loadAndProcessDemo, calculateMetrics } from '@/lib/demoLoader'
import type { DemoMetadata, DemoStep } from '@/lib/types'

export default function ShowcasePage() {
	const [demos, setDemos] = useState<DemoMetadata[]>([])
	const [selectedDemoId, setSelectedDemoId] = useState<string | null>(null)
	const [demoSteps, setDemoSteps] = useState<DemoStep[] | null>(null)
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState<string | null>(null)
	const [activeTab, setActiveTab] = useState<'player' | 'metrics' | 'code'>('player')

	// Load demo manifest on mount
	useEffect(() => {
		loadDemoManifest()
			.then((manifest) => {
				setDemos(manifest.demos)
				// Auto-select first demo
				if (manifest.demos.length > 0) {
					setSelectedDemoId(manifest.demos[0].id)
				}
				setLoading(false)
			})
			.catch((err) => {
				console.error('Failed to load demos:', err)
				setError('Failed to load demos')
				setLoading(false)
			})
	}, [])

	// Load selected demo
	useEffect(() => {
		if (!selectedDemoId) return

		setDemoSteps(null)
		setLoading(true)

		loadAndProcessDemo(selectedDemoId)
			.then((steps) => {
				setDemoSteps(steps)
				setLoading(false)
			})
			.catch((err) => {
				console.error('Failed to load demo:', err)
				setError('Failed to load demo trajectory')
				setLoading(false)
			})
	}, [selectedDemoId])

	const selectedDemo = demos.find((d) => d.id === selectedDemoId)

	if (loading && demos.length === 0) {
		return (
			<main className="min-h-screen bg-gray-900 text-white">
				<div className="bg-gray-800 border-b border-gray-700">
					<div className="container mx-auto px-6 py-6">
						<div className="flex items-center justify-between mb-4">
							<div className="h-8 bg-gray-700 rounded w-48 animate-pulse"></div>
							<Link href="/" className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors">
								← Back to Home
							</Link>
						</div>
						<DemoSelectorSkeleton />
					</div>
				</div>
				<div className="container mx-auto px-6 py-8">
					<TrajectoryPlayerSkeleton />
				</div>
			</main>
		)
	}

	if (error) {
		return (
			<main className="min-h-screen bg-gray-900 text-white p-8">
				<div className="container mx-auto">
					<div className="bg-red-900 bg-opacity-20 border border-red-700 rounded-lg p-6">
						<h2 className="text-xl font-semibold text-red-400 mb-2">Error</h2>
						<p className="text-gray-300">{error}</p>
					</div>
				</div>
			</main>
		)
	}

	const metrics = demoSteps ? calculateMetrics(demoSteps) : null

	return (
		<main className="min-h-screen bg-gray-900 text-white" role="main">
			{/* Skip to main content link */}
			<a
				href="#demo-content"
				className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded"
			>
				Skip to demo content
			</a>

			{/* Header */}
			<div className="bg-gray-800 border-b border-gray-700">
				<div className="container mx-auto px-6 py-6">
					<div className="flex items-center justify-between mb-4">
						<h1 className="text-3xl font-bold">Demo Showcase</h1>
						<Link
							href="/"
							className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
							aria-label="Navigate back to home page"
						>
							← Back to Home
						</Link>
					</div>

					{/* Demo Selector */}
					<div className="flex gap-2 overflow-x-auto" role="navigation" aria-label="Demo selection">
						{demos.map((demo) => (
							<button
								key={demo.id}
								onClick={() => setSelectedDemoId(demo.id)}
								className={`flex-shrink-0 px-6 py-3 rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
									selectedDemoId === demo.id
										? 'bg-blue-600 text-white'
										: 'bg-gray-700 text-gray-300 hover:bg-gray-600'
								}`}
								aria-pressed={selectedDemoId === demo.id}
								aria-label={`Select ${demo.title} demo, ${demo.metrics.steps} steps, ${demo.metrics.tokens.toLocaleString()} tokens`}
							>
								<div className="text-sm">{demo.title}</div>
								<div className="text-xs mt-1 opacity-75" aria-hidden="true">
									{demo.metrics.steps} steps • {demo.metrics.tokens.toLocaleString()} tokens
								</div>
							</button>
						))}
					</div>
				</div>
			</div>

			{/* Main Content */}
			<div className="container mx-auto px-6 py-8">
				{selectedDemo && (
					<div className="mb-6">
						<h2 className="text-2xl font-semibold mb-2">{selectedDemo.title}</h2>
						<p className="text-gray-400">{selectedDemo.description}</p>
						<div className="mt-2 flex gap-4 text-sm">
							<span className="text-gray-400">
								Task: <span className="text-white">{selectedDemo.task}</span>
							</span>
						</div>
					</div>
				)}

				{/* Tabs */}
				<div className="flex gap-2 mb-6" role="tablist" aria-label="Demo view options">
					<button
						onClick={() => setActiveTab('player')}
						className={`px-6 py-3 rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
							activeTab === 'player'
								? 'bg-blue-600 text-white'
								: 'bg-gray-800 text-gray-300 hover:bg-gray-700'
						}`}
						role="tab"
						aria-selected={activeTab === 'player'}
						aria-controls="player-panel"
						id="player-tab"
					>
						Player
					</button>
					<button
						onClick={() => setActiveTab('metrics')}
						className={`px-6 py-3 rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
							activeTab === 'metrics'
								? 'bg-blue-600 text-white'
								: 'bg-gray-800 text-gray-300 hover:bg-gray-700'
						}`}
						role="tab"
						aria-selected={activeTab === 'metrics'}
						aria-controls="metrics-panel"
						id="metrics-tab"
					>
						Metrics
					</button>
					<button
						onClick={() => setActiveTab('code')}
						className={`px-6 py-3 rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
							activeTab === 'code'
								? 'bg-blue-600 text-white'
								: 'bg-gray-800 text-gray-300 hover:bg-gray-700'
						}`}
						role="tab"
						aria-selected={activeTab === 'code'}
						aria-controls="code-panel"
						id="code-tab"
					>
						Code
					</button>
				</div>

				{/* Tab Content */}
				{loading && !demoSteps ? (
					<div>
						{activeTab === 'player' && <TrajectoryPlayerSkeleton />}
						{activeTab === 'metrics' && <ChartSkeleton />}
						{activeTab === 'code' && (
							<div className="space-y-4">
								<CodeBlockSkeleton />
								<CodeBlockSkeleton />
							</div>
						)}
					</div>
				) : (
					demoSteps &&
					selectedDemo && (
						<AnimatePresence mode="wait">
							{activeTab === 'player' && (
								<motion.div
									key="player"
									initial={{ opacity: 0, x: -20 }}
									animate={{ opacity: 1, x: 0 }}
									exit={{ opacity: 0, x: 20 }}
									transition={{ duration: 0.3 }}
									role="tabpanel"
									id="player-panel"
									aria-labelledby="player-tab"
								>
									<TrajectoryPlayer
										steps={demoSteps}
										title={selectedDemo.title}
										mode={selectedDemo.mode}
										videoUrl={selectedDemo.video_url}
									/>
								</motion.div>
							)}

							{activeTab === 'metrics' && metrics && (
								<motion.div
									key="metrics"
									initial={{ opacity: 0, x: -20 }}
									animate={{ opacity: 1, x: 0 }}
									exit={{ opacity: 0, x: 20 }}
									transition={{ duration: 0.3 }}
									role="tabpanel"
									id="metrics-panel"
									aria-labelledby="metrics-tab"
								>
									<MetricsVisualization
										steps={demoSteps}
										totalMetrics={metrics}
										mode={selectedDemo.mode}
									/>
								</motion.div>
							)}

							{activeTab === 'code' && (
								<motion.div
									key="code"
									initial={{ opacity: 0, x: -20 }}
									animate={{ opacity: 1, x: 0 }}
									exit={{ opacity: 0, x: 20 }}
									transition={{ duration: 0.3 }}
									className="space-y-4"
									role="tabpanel"
									id="code-panel"
									aria-labelledby="code-tab"
								>
									<CodeBlock
										code={demoSteps[0].actionDetails}
										title="Example Action (Step 1)"
										language="json"
									/>
									<CodeBlock
										code={{
											steps: demoSteps.length,
											totalTokens: metrics?.tokens,
											totalCost: metrics?.cost,
											duration: metrics?.duration,
										}}
										title="Summary Metrics"
										language="json"
									/>
								</motion.div>
							)}
						</AnimatePresence>
					)
				)}
			</div>
		</main>
	)
}
