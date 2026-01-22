'use client'

import { useState, useEffect } from 'react'
import type { DemoStep } from '@/lib/types'

interface TrajectoryPlayerProps {
	steps: DemoStep[]
	title: string
	mode: string
	videoUrl?: string // Optional video URL for traditional mode
}

export default function TrajectoryPlayer({ steps, title, mode, videoUrl }: TrajectoryPlayerProps) {
	const [currentStepIndex, setCurrentStepIndex] = useState(0)
	const [isPlaying, setIsPlaying] = useState(false)
	const [playbackSpeed, setPlaybackSpeed] = useState(1) // 1x, 2x, 4x

	const currentStep = steps[currentStepIndex]
	const progress = ((currentStepIndex + 1) / steps.length) * 100

	// Auto-play functionality
	useEffect(() => {
		if (!isPlaying) return

		const interval = setInterval(() => {
			setCurrentStepIndex((prev) => {
				if (prev >= steps.length - 1) {
					setIsPlaying(false)
					return prev
				}
				return prev + 1
			})
		}, 2000 / playbackSpeed) // 2 seconds per step, adjusted by speed

		return () => clearInterval(interval)
	}, [isPlaying, playbackSpeed, steps.length])

	const handlePlayPause = () => {
		if (currentStepIndex >= steps.length - 1) {
			// Reset to beginning if at end
			setCurrentStepIndex(0)
		}
		setIsPlaying(!isPlaying)
	}

	const handlePrevious = () => {
		setCurrentStepIndex((prev) => Math.max(0, prev - 1))
		setIsPlaying(false)
	}

	const handleNext = () => {
		setCurrentStepIndex((prev) => Math.min(steps.length - 1, prev + 1))
		setIsPlaying(false)
	}

	const handleStepClick = (index: number) => {
		setCurrentStepIndex(index)
		setIsPlaying(false)
	}

	const cycleSpe = () => {
		setPlaybackSpeed((prev) => {
			if (prev === 1) return 2
			if (prev === 2) return 4
			return 1
		})
	}

	return (
		<div className="bg-gray-800 rounded-lg overflow-hidden" role="region" aria-label="Demo trajectory player">
			{/* Header */}
			<div className="bg-gray-900 px-6 py-4 border-b border-gray-700">
				<h3 className="text-xl font-semibold text-white">{title}</h3>
				<p className="text-sm text-gray-400 mt-1">
					Mode: <span className="text-blue-400 font-medium">{mode}</span>
				</p>
			</div>

			{/* Main Content */}
			<div className="p-6">
				{/* Step Info */}
				<div className="mb-4">
					<div className="flex justify-between items-center mb-2">
						<span className="text-lg font-semibold text-white" aria-live="polite">
							Step {currentStep.stepNumber} of {steps.length}
						</span>
						<span className="text-sm text-gray-400">
							{currentStep.duration.toFixed(1)}s
						</span>
					</div>

					{/* Progress Bar */}
					<div
						className="w-full bg-gray-700 rounded-full h-2 mb-4"
						role="progressbar"
						aria-valuenow={currentStepIndex + 1}
						aria-valuemin={1}
						aria-valuemax={steps.length}
						aria-label={`Demo progress: step ${currentStepIndex + 1} of ${steps.length}`}
					>
						<div
							className="bg-blue-500 h-2 rounded-full transition-all duration-300"
							style={{ width: `${progress}%` }}
						/>
					</div>
				</div>

				{/* Action */}
				<div className="mb-4">
					<h4 className="text-sm font-semibold text-gray-400 mb-2">Action:</h4>
					<div className="bg-gray-900 rounded p-3">
						<p className="text-white font-mono text-sm">{currentStep.action}</p>
					</div>
				</div>

				{/* Result */}
				<div className="mb-6">
					<h4 className="text-sm font-semibold text-gray-400 mb-2">Result:</h4>
					<div className="bg-gray-900 rounded p-3 max-h-32 overflow-y-auto">
						<p className="text-gray-300 text-sm whitespace-pre-wrap">
							{currentStep.result || 'No result content'}
						</p>
					</div>
				</div>

				{/* Video Player (for traditional mode) or Screenshot */}
				{videoUrl && mode === 'traditional' ? (
					<div className="mb-6">
						<h4 className="text-sm font-semibold text-gray-400 mb-2">Demo Recording:</h4>
						<div className="bg-gray-900 rounded p-2">
							<video
								key={videoUrl}
								controls
								className="w-full h-auto rounded"
								style={{ maxHeight: '500px' }}
							>
								<source src={videoUrl} type="video/webm" />
								<source src={videoUrl.replace('.webm', '.mp4')} type="video/mp4" />
								Your browser does not support the video tag.
							</video>
							<p className="text-xs text-gray-500 mt-2 text-center">
								Video shows actual browser navigation during execution
							</p>
						</div>
					</div>
				) : currentStep.screenshot ? (
					<div className="mb-6">
						<h4 className="text-sm font-semibold text-gray-400 mb-2">Screenshot:</h4>
						<div className="bg-gray-900 rounded p-4 text-center">
							<img
								src={currentStep.screenshot}
								alt={`Step ${currentStep.stepNumber} screenshot`}
								className="max-w-full h-auto mx-auto rounded"
							/>
						</div>
					</div>
				) : (
					<div className="mb-6">
						<div className="bg-gray-900 rounded p-8 text-center">
							<p className="text-gray-500 text-sm">No video or screenshot available</p>
						</div>
					</div>
				)}

				{/* Controls */}
				<div className="flex items-center justify-between" role="group" aria-label="Playback controls">
					<div className="flex gap-2">
						<button
							onClick={handlePrevious}
							disabled={currentStepIndex === 0}
							className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
							aria-label="Go to previous step"
						>
							← Previous
						</button>
						<button
							onClick={handlePlayPause}
							className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
							aria-label={isPlaying ? 'Pause playback' : 'Play demo'}
						>
							{isPlaying ? '⏸ Pause' : '▶️ Play'}
						</button>
						<button
							onClick={handleNext}
							disabled={currentStepIndex >= steps.length - 1}
							className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
							aria-label="Go to next step"
						>
							Next →
						</button>
					</div>

					<button
						onClick={cycleSpe}
						className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
						aria-label={`Change playback speed. Current speed: ${playbackSpeed}x`}
					>
						{playbackSpeed}x Speed
					</button>
				</div>

				{/* Step Timeline */}
				<div className="mt-6 pt-6 border-t border-gray-700">
					<h4 className="text-sm font-semibold text-gray-400 mb-3">Timeline:</h4>
					<div className="flex gap-2 overflow-x-auto pb-2" role="group" aria-label="Step timeline navigation">
						{steps.map((step, index) => (
							<button
								key={index}
								onClick={() => handleStepClick(index)}
								className={`flex-shrink-0 min-w-[44px] min-h-[44px] w-12 h-12 rounded flex items-center justify-center text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
									index === currentStepIndex
										? 'bg-blue-600 text-white'
										: index < currentStepIndex
											? 'bg-green-700 text-white hover:bg-green-600'
											: 'bg-gray-700 text-gray-400 hover:bg-gray-600'
								}`}
								aria-label={`Go to step ${step.stepNumber}`}
								aria-current={index === currentStepIndex ? 'step' : undefined}
							>
								{step.stepNumber}
							</button>
						))}
					</div>
				</div>
			</div>
		</div>
	)
}
