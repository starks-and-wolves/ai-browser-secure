'use client'

import { motion } from 'framer-motion'

export function MetricsCardSkeleton() {
	return (
		<motion.div
			className="bg-gray-800 rounded-lg p-4 animate-pulse"
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			exit={{ opacity: 0 }}
		>
			<div className="h-3 bg-gray-700 rounded w-16 mb-2"></div>
			<div className="h-8 bg-gray-700 rounded w-24"></div>
		</motion.div>
	)
}

export function TrajectoryPlayerSkeleton() {
	return (
		<motion.div
			className="bg-gray-800 rounded-lg p-6 space-y-4"
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			exit={{ opacity: 0 }}
		>
			{/* Progress bar skeleton */}
			<div className="h-2 bg-gray-700 rounded animate-pulse"></div>

			{/* Screenshot skeleton */}
			<div className="bg-gray-900 rounded-lg aspect-video flex items-center justify-center animate-pulse">
				<div className="text-gray-600">Loading screenshot...</div>
			</div>

			{/* Action display skeleton */}
			<div className="space-y-2">
				<div className="h-6 bg-gray-700 rounded w-3/4 animate-pulse"></div>
				<div className="h-4 bg-gray-700 rounded w-1/2 animate-pulse"></div>
			</div>

			{/* Controls skeleton */}
			<div className="flex justify-center gap-4 pt-4">
				<div className="h-10 bg-gray-700 rounded w-24 animate-pulse"></div>
				<div className="h-10 bg-gray-700 rounded w-24 animate-pulse"></div>
				<div className="h-10 bg-gray-700 rounded w-24 animate-pulse"></div>
			</div>

			{/* Timeline skeleton */}
			<div className="flex gap-1 pt-4">
				{Array.from({ length: 8 }).map((_, i) => (
					<div key={i} className="flex-1 h-2 bg-gray-700 rounded animate-pulse"></div>
				))}
			</div>
		</motion.div>
	)
}

export function CodeBlockSkeleton() {
	return (
		<motion.div
			className="bg-gray-900 rounded-lg border border-gray-700 animate-pulse"
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			exit={{ opacity: 0 }}
		>
			{/* Header */}
			<div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
				<div className="h-4 bg-gray-700 rounded w-32"></div>
				<div className="h-6 bg-gray-700 rounded w-16"></div>
			</div>

			{/* Code content */}
			<div className="p-4 space-y-2">
				{Array.from({ length: 8 }).map((_, i) => (
					<div key={i} className="h-4 bg-gray-800 rounded" style={{ width: `${Math.random() * 40 + 60}%` }}></div>
				))}
			</div>
		</motion.div>
	)
}

export function DemoSelectorSkeleton() {
	return (
		<div className="flex gap-2 overflow-x-auto">
			{Array.from({ length: 3 }).map((_, i) => (
				<div key={i} className="flex-shrink-0 px-6 py-3 bg-gray-700 rounded-lg animate-pulse">
					<div className="h-4 bg-gray-600 rounded w-32 mb-2"></div>
					<div className="h-3 bg-gray-600 rounded w-24"></div>
				</div>
			))}
		</div>
	)
}

export function ChartSkeleton() {
	return (
		<motion.div
			className="bg-gray-800 rounded-lg p-6 space-y-4"
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			exit={{ opacity: 0 }}
		>
			<div className="h-6 bg-gray-700 rounded w-48 mb-4 animate-pulse"></div>
			<div className="relative h-48 flex items-end justify-between gap-1">
				{Array.from({ length: 10 }).map((_, i) => (
					<div
						key={i}
						className="flex-1 bg-gray-700 rounded-t animate-pulse"
						style={{ height: `${Math.random() * 60 + 40}%` }}
					></div>
				))}
			</div>
		</motion.div>
	)
}
