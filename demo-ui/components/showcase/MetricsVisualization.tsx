'use client'

import type { DemoStep } from '@/lib/types'

interface MetricsVisualizationProps {
	steps: DemoStep[]
	totalMetrics: {
		steps: number
		tokens: number
		duration: number
		cost: number
	}
	mode: string
}

export default function MetricsVisualization({ steps, totalMetrics, mode }: MetricsVisualizationProps) {
	// Calculate cumulative tokens for each step
	const cumulativeTokens = steps.reduce<number[]>((acc, step) => {
		const prev = acc.length > 0 ? acc[acc.length - 1] : 0
		acc.push(prev + (step.tokensUsed || 0))
		return acc
	}, [])

	const maxTokens = cumulativeTokens[cumulativeTokens.length - 1] || 1

	return (
		<div className="space-y-6">
			{/* Key Metrics Cards */}
			<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
				<div className="bg-gray-800 rounded-lg p-4">
					<div className="text-gray-400 text-sm mb-1">Steps</div>
					<div className="text-2xl font-bold text-white">{totalMetrics.steps}</div>
				</div>
				<div className="bg-gray-800 rounded-lg p-4">
					<div className="text-gray-400 text-sm mb-1">Tokens</div>
					<div className="text-2xl font-bold text-blue-400">
						{totalMetrics.tokens.toLocaleString()} 🪙
					</div>
				</div>
				<div className="bg-gray-800 rounded-lg p-4">
					<div className="text-gray-400 text-sm mb-1">Cost</div>
					<div className="text-2xl font-bold text-green-400">
						${totalMetrics.cost.toFixed(3)}
					</div>
				</div>
				<div className="bg-gray-800 rounded-lg p-4">
					<div className="text-gray-400 text-sm mb-1">Duration</div>
					<div className="text-2xl font-bold text-purple-400">
						{totalMetrics.duration.toFixed(1)}s
					</div>
				</div>
			</div>

			{/* Token Usage Chart */}
			<div className="bg-gray-800 rounded-lg p-6">
				<h4 className="text-lg font-semibold text-white mb-4">
					Cumulative Token Usage
				</h4>

				<div className="relative h-48">
					{/* Y-axis labels */}
					<div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-sm text-gray-400">
						<span>{maxTokens.toLocaleString()}</span>
						<span>{Math.floor(maxTokens / 2).toLocaleString()}</span>
						<span>0</span>
					</div>

					{/* Chart area */}
					<div className="absolute left-14 right-0 top-0 bottom-6 flex items-end justify-between gap-1">
						{cumulativeTokens.map((tokens, index) => {
							const height = (tokens / maxTokens) * 100
							return (
								<div key={index} className="flex-1 flex flex-col justify-end group relative">
									<div
										className="bg-blue-500 hover:bg-blue-400 transition-all rounded-t w-full"
										style={{ height: `${height}%` }}
									>
										{/* Tooltip */}
										<div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 hidden group-hover:block bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-nowrap z-10">
											Step {index + 1}: {tokens.toLocaleString()} tokens
										</div>
									</div>
								</div>
							)
						})}
					</div>

					{/* X-axis */}
					<div className="absolute bottom-0 left-14 right-0 h-6 flex justify-between text-sm text-gray-400">
						<span>1</span>
						{steps.length > 2 && (
							<span className="hidden md:inline">{Math.floor(steps.length / 2)}</span>
						)}
						<span>{steps.length}</span>
					</div>
				</div>

				<div className="mt-4 text-sm text-gray-400 text-center">
					Steps
				</div>
			</div>

			{/* Step-by-Step Breakdown */}
			<div className="bg-gray-800 rounded-lg p-6">
				<h4 className="text-lg font-semibold text-white mb-4">
					Step Breakdown
				</h4>

				<div className="space-y-2">
					{steps.map((step) => (
						<div
							key={step.stepNumber}
							className="flex items-center justify-between py-2 px-3 bg-gray-900 rounded hover:bg-gray-750 transition-colors"
						>
							<div className="flex items-center gap-3">
								<div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center text-sm font-semibold">
									{step.stepNumber}
								</div>
								<div className="text-sm text-gray-300 truncate max-w-md">
									{step.action}
								</div>
							</div>
							<div className="flex items-center gap-6 text-sm">
								<span className="text-gray-400">
									{(step.tokensUsed || 0).toLocaleString()} 🪙
								</span>
								<span className="text-gray-400">
									{step.duration.toFixed(1)}s
								</span>
							</div>
						</div>
					))}
				</div>
			</div>

			{/* Mode-specific Notes */}
			{mode === 'awi' && (
				<div className="bg-green-900 bg-opacity-20 border border-green-700 rounded-lg p-4">
					<h5 className="text-green-400 font-semibold mb-2">AWI Mode Benefits</h5>
					<ul className="text-sm text-gray-300 space-y-1">
						<li>• Direct API calls instead of DOM parsing</li>
						<li>• ~500x token reduction vs traditional mode</li>
						<li>• Structured responses with metadata</li>
						<li>• Server-side session state tracking</li>
					</ul>
				</div>
			)}
		</div>
	)
}
