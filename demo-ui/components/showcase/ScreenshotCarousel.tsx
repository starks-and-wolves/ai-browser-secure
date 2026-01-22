'use client'

import { useState } from 'react'
import type { DemoStep } from '@/lib/types'

interface ScreenshotCarouselProps {
	steps: DemoStep[]
}

export default function ScreenshotCarousel({ steps }: ScreenshotCarouselProps) {
	const [currentIndex, setCurrentIndex] = useState(0)

	// Filter steps that have screenshots
	const stepsWithScreenshots = steps.filter((step) => step.screenshot)

	if (stepsWithScreenshots.length === 0) {
		return (
			<div className="bg-gray-800 rounded-lg p-8 text-center">
				<p className="text-gray-400">No screenshots available for this demo</p>
			</div>
		)
	}

	const currentStep = stepsWithScreenshots[currentIndex]

	const handlePrevious = () => {
		setCurrentIndex((prev) => (prev > 0 ? prev - 1 : stepsWithScreenshots.length - 1))
	}

	const handleNext = () => {
		setCurrentIndex((prev) => (prev < stepsWithScreenshots.length - 1 ? prev + 1 : 0))
	}

	return (
		<div className="bg-gray-800 rounded-lg overflow-hidden">
			{/* Header */}
			<div className="px-6 py-4 bg-gray-900 border-b border-gray-700">
				<div className="flex items-center justify-between">
					<h4 className="text-lg font-semibold text-white">Screenshots</h4>
					<span className="text-sm text-gray-400">
						{currentIndex + 1} of {stepsWithScreenshots.length}
					</span>
				</div>
			</div>

			{/* Main Image */}
			<div className="relative bg-black">
				<img
					src={currentStep.screenshot}
					alt={`Step ${currentStep.stepNumber} screenshot`}
					className="w-full h-auto max-h-96 object-contain"
				/>

				{/* Navigation Arrows */}
				{stepsWithScreenshots.length > 1 && (
					<>
						<button
							onClick={handlePrevious}
							className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white p-3 rounded-full transition-all"
						>
							←
						</button>
						<button
							onClick={handleNext}
							className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white p-3 rounded-full transition-all"
						>
							→
						</button>
					</>
				)}
			</div>

			{/* Step Info */}
			<div className="px-6 py-4 bg-gray-900">
				<div className="text-sm text-gray-400 mb-1">
					Step {currentStep.stepNumber}
				</div>
				<div className="text-white font-medium">{currentStep.action}</div>
			</div>

			{/* Thumbnail Timeline */}
			{stepsWithScreenshots.length > 1 && (
				<div className="px-6 py-4 border-t border-gray-700">
					<div className="flex gap-2 overflow-x-auto">
						{stepsWithScreenshots.map((step, index) => (
							<button
								key={index}
								onClick={() => setCurrentIndex(index)}
								className={`flex-shrink-0 w-16 h-16 rounded overflow-hidden border-2 transition-all ${
									index === currentIndex
										? 'border-blue-500 scale-110'
										: 'border-gray-600 hover:border-gray-500 opacity-60 hover:opacity-100'
								}`}
							>
								<img
									src={step.screenshot}
									alt={`Step ${step.stepNumber} thumbnail`}
									className="w-full h-full object-cover"
								/>
							</button>
						))}
					</div>
				</div>
			)}
		</div>
	)
}
