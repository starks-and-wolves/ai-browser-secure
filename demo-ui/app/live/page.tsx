'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { LiveDemoClient, type LiveDemoMessage } from '@/lib/websocket'
import { checkBackendHealth, startLiveDemo as apiStartLiveDemo, getApiUrl, getDiagnosticInfo } from '@/lib/api'

type ExecutionStatus = 'idle' | 'connecting' | 'running' | 'completed' | 'error'

interface LogEntry {
	timestamp: number
	type: string
	message: string
}

export default function LiveDemoPage() {
	// Auto-detect backend URL from environment or infer from hostname
	const getDefaultBackendUrl = () => {
		// Check environment variable first
		const envUrl = process.env.NEXT_PUBLIC_API_URL
		if (envUrl && envUrl !== 'http://localhost:8000') {
			return envUrl
		}

		// If running on Replit, try to infer backend URL
		if (typeof window !== 'undefined') {
			const hostname = window.location.hostname

			// Pattern: frontend-name.username.repl.co -> backend-name.username.repl.co
			if (hostname.includes('.repl.co') || hostname.includes('.replit.dev')) {
				const parts = hostname.split('.')
				if (parts.length >= 3) {
					// Replace frontend name with backend name
					const backendHostname = hostname.replace(/^[^.]+/, 'browser-use-backend')
					return `https://${backendHostname}`
				}
			}
		}

		// Default fallback
		return 'http://localhost:8000'
	}

	// Form state
	const [apiKey, setApiKey] = useState('')
	const [task, setTask] = useState('List the top 3 blog posts, then add a comment, \'Great post!\' to the first one. After adding the comment, end the process')
	const [targetUrl, setTargetUrl] = useState('https://blog.anthropic.com')
	const [backendUrl, setBackendUrl] = useState(getDefaultBackendUrl())
	const [showBackendConfig, setShowBackendConfig] = useState(false)

	// AWI Registration config (for headless mode)
	const [awiAgentName, setAwiAgentName] = useState('BrowserUseAgent')
	const [awiPermissions, setAwiPermissions] = useState<string[]>(['read', 'write'])
	const [showAwiConfig, setShowAwiConfig] = useState(false)

	// Execution state
	const [status, setStatus] = useState<ExecutionStatus>('idle')
	const [logs, setLogs] = useState<LogEntry[]>([])
	const [currentStep, setCurrentStep] = useState(0)
	const [currentAction, setCurrentAction] = useState<string>('')
	const [metrics, setMetrics] = useState<{
		tokens: number
		prompt_tokens?: number
		completion_tokens?: number
		steps: number
		cost: number
		duration?: number
	} | null>(null)
	const [completionResult, setCompletionResult] = useState<{
		success: boolean
		result?: string
		totalSteps: number
	} | null>(null)

	// WebSocket client
	const [wsClient, setWsClient] = useState<LiveDemoClient | null>(null)

	// Set pre-configured URL for AWI mode
	useEffect(() => {
		setTargetUrl('https://ai-browser-security.onrender.com/')
		setShowAwiConfig(true) // Show AWI config by default in AWI mode
	}, [])

	const addLog = (type: string, message: string) => {
		setLogs((prev) => [
			...prev,
			{ timestamp: Date.now(), type, message },
		])
	}

	const startDemo = async () => {
		if (!apiKey) {
			alert('Please enter your API key')
			return
		}

		setStatus('connecting')
		setLogs([])
		setCurrentStep(0)
		setCurrentAction('')
		setMetrics(null)
		setCompletionResult(null)

		try {
			// Step 1: Check backend health
			addLog('info', 'Checking backend connection...')
			addLog('info', `Backend URL: ${backendUrl}`)

			const healthCheck = await checkBackendHealth(backendUrl)

			if (!healthCheck.reachable) {
				addLog('error', `Backend health check failed: ${healthCheck.error}`)
				addLog('error', 'Troubleshooting tips:')
				addLog('error', '1. Check if backend is running')
				addLog('error', '2. Click "Backend Settings" to verify/update backend URL')
				addLog('error', '3. Check browser console for CORS errors')
				addLog('error', `4. Current backend URL: ${backendUrl}`)
				setStatus('error')
				return
			}

			addLog('info', `Backend is reachable (${healthCheck.latency}ms)`)

			// Step 2: Start session on backend
			addLog('info', 'Starting session...')
			const result = await apiStartLiveDemo({
				task,
				mode: 'awi',
				targetUrl,
				apiKey,
				backendUrl,
				// Pass AWI registration config
				awiConfig: {
					agent_name: awiAgentName,
					permissions: awiPermissions,
					auto_approve: true,
				},
			})

			if (!result.success || !result.sessionId) {
				addLog('error', `Failed to start session: ${result.error}`)
				setStatus('error')
				return
			}

			addLog('info', `Session created: ${result.sessionId}`)

			// Step 3: Connect WebSocket
			addLog('info', 'Connecting WebSocket...')
			const client = new LiveDemoClient(result.sessionId, backendUrl)
			setWsClient(client)

			await client.connect(
				(message: LiveDemoMessage) => {
					handleWebSocketMessage(message)
				},
				(error) => {
					addLog('error', `WebSocket error: ${error}`)
					setStatus('error')
				}
			)

			addLog('info', 'WebSocket connected')

			// Step 4: Send API key
			client.sendApiKey(apiKey)
			setStatus('running')
			addLog('info', 'Demo started!')
		} catch (error) {
			if (error instanceof Error) {
				addLog('error', `Failed to start: ${error.message}`)

				// Provide specific troubleshooting for common errors
				if (error.message.includes('Failed to fetch')) {
					addLog('error', 'This is usually a CORS or network issue.')
					addLog('error', 'Check:')
					addLog('error', '1. Is the backend running?')
					addLog('error', '2. Is NEXT_PUBLIC_API_URL correct?')
					addLog('error', '3. Check browser console for detailed error')
				}
			} else {
				addLog('error', `Failed to start: ${error}`)
			}
			setStatus('error')
		}
	}

	const handleWebSocketMessage = (message: LiveDemoMessage) => {
		switch (message.type) {
			case 'ready':
				addLog('info', message.message || 'Ready to start')
				break

			case 'status':
				addLog('status', message.message || '')
				break

			case 'log':
				// Backend log message - map log level to display type
				const logType = message.level === 'ERROR' ? 'error'
					: message.level === 'WARNING' ? 'warning'
					: message.level === 'INFO' && message.message?.includes('✅') ? 'success'
					: message.level === 'INFO' && message.message?.includes('📍') ? 'step'
					: 'info'

				// Extract step number from messages like "📍 Step 1:"
				if (message.message?.includes('📍 Step')) {
					const stepMatch = message.message.match(/📍 Step (\d+):/)
					if (stepMatch) {
						const stepNum = parseInt(stepMatch[1], 10)
						setCurrentStep(stepNum)
						// Update step count in metrics
						setMetrics((prev) => ({
							tokens: prev?.tokens || 0,
							prompt_tokens: prev?.prompt_tokens,
							completion_tokens: prev?.completion_tokens,
							steps: stepNum,
							cost: prev?.cost || 0,
							duration: prev?.duration,
						}))
					}
				}

				// Extract current action/goal from "🎯 Next goal:" messages
				if (message.message?.includes('🎯 Next goal:')) {
					const goalMatch = message.message.match(/🎯 Next goal:\s*(.+)$/)
					if (goalMatch) {
						// Remove ANSI color codes and trim
						const goal = goalMatch[1].replace(/\[[\d;]+m/g, '').trim()
						setCurrentAction(goal)
					}
				}

				addLog(logType, message.message || '')
				break

			case 'agent_started':
				addLog('success', 'Agent execution started')
				// Initialize metrics tracking
				setMetrics({
					tokens: 0,
					steps: 0,
					cost: 0,
				})
				break

			case 'step':
				const stepNumber = message.step_number || 0
				setCurrentStep(stepNumber)
				addLog('step', `Step ${message.step_number}: ${message.action}`)
				// Update step count in metrics
				setMetrics((prev) => ({
					tokens: prev?.tokens || 0,
					prompt_tokens: prev?.prompt_tokens,
					completion_tokens: prev?.completion_tokens,
					steps: stepNumber,
					cost: prev?.cost || 0,
					duration: prev?.duration,
				}))
				break

			case 'completed':
				addLog(
					message.success ? 'success' : 'warning',
					`Execution ${message.success ? 'completed successfully' : 'failed'} (${message.total_steps} steps)`
				)
				setStatus('completed')
				setCompletionResult({
					success: message.success || false,
					result: message.result,
					totalSteps: message.total_steps || 0,
				})
				// Ensure final step count is recorded in metrics
				setMetrics((prev) => ({
					tokens: prev?.tokens || 0,
					prompt_tokens: prev?.prompt_tokens,
					completion_tokens: prev?.completion_tokens,
					steps: message.total_steps || prev?.steps || 0,
					cost: prev?.cost || 0,
					duration: prev?.duration,
				}))
				break

			case 'metrics':
				setMetrics({
					tokens: message.tokens || 0,
					prompt_tokens: message.prompt_tokens,
					completion_tokens: message.completion_tokens,
					steps: message.steps || 0,
					cost: message.cost || 0,
					duration: message.duration,
				})
				const costDisplay = message.cost && message.cost > 0 ? `$${message.cost.toFixed(4)}` : '$0.0000'
				addLog('info', `Metrics: ${message.tokens || 0} tokens, ${costDisplay}`)
				break

			case 'agent_registry':
				// Agent registry info is also sent as log messages
				if (message.message) {
					addLog('info', message.message)
				}
				break

			case 'error':
				addLog('error', message.message || 'Unknown error')
				setStatus('error')
				// Keep metrics visible even on error
				break
		}
	}

	const stopDemo = () => {
		if (wsClient) {
			wsClient.disconnect()
			setWsClient(null)
		}
		setStatus('error')
		addLog('warning', `Demo stopped manually after ${currentStep} steps`)
		// Metrics are preserved and will remain visible
		setCompletionResult({
			success: false,
			result: 'Execution stopped by user',
			totalSteps: currentStep,
		})
	}

	return (
		<main className="min-h-screen bg-gray-900 text-white" role="main">
			{/* Header */}
			<div className="bg-gray-800 border-b border-gray-700">
				<div className="container mx-auto px-6 py-6">
					<div className="flex items-center justify-between">
						<div>
							<h1 className="text-3xl font-bold">Live Demo</h1>
							<p className="text-gray-400 mt-1">
								Run browser-use agent with AWI mode
							</p>
						</div>
						<div className="flex items-center gap-4">
							{/* Step Counter - Top Right */}
							{status === 'running' && currentStep > 0 && (
								<div className="flex items-center gap-2 px-4 py-2 bg-gray-900 rounded-lg">
									<div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
									<span className="text-sm text-green-400 font-semibold">Step {currentStep}</span>
								</div>
							)}
							{status === 'completed' && completionResult?.success && (
								<div className="flex items-center gap-2 px-4 py-2 bg-gray-900 rounded-lg">
									<div className="w-2 h-2 bg-green-500 rounded-full"></div>
									<span className="text-sm text-green-400 font-semibold">✅ Completed ({completionResult.totalSteps} steps)</span>
								</div>
							)}
							{status === 'error' && completionResult && (
								<div className="flex items-center gap-2 px-4 py-2 bg-gray-900 rounded-lg">
									<div className="w-2 h-2 bg-orange-500 rounded-full"></div>
									<span className="text-sm text-orange-400 font-semibold">
										{completionResult.result === 'Execution stopped by user' ? '⏸️ Stopped' : '❌ Failed'} ({completionResult.totalSteps} steps)
									</span>
								</div>
							)}
							<Link
								href="/"
								className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
							>
								← Back to Home
							</Link>
						</div>
					</div>
				</div>
			</div>

			<div className="container mx-auto px-6 py-8">
				<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
					{/* Left: Configuration */}
					<motion.div
						initial={{ opacity: 0, x: -20 }}
						animate={{ opacity: 1, x: 0 }}
						transition={{ duration: 0.5 }}
					>
						<div className="bg-gray-800 rounded-lg p-6 space-y-6">
							<h2 className="text-xl font-semibold">Configuration</h2>

							{/* Demo Warning Note */}
							<div className="bg-yellow-900/30 border border-yellow-500/50 rounded-lg p-4">
								<div className="flex items-start gap-3">
									<span className="text-yellow-400 text-lg">⚠️</span>
									<div className="text-sm text-yellow-200">
										<p className="font-medium mb-1">Demo Environment Notice</p>
										<p className="text-yellow-300/80">
											This is a demo website running on limited resources. Some actions may cause resource spikes and might not complete successfully. For production use, please deploy with adequate resources.
										</p>
									</div>
								</div>
							</div>

							{/* Target URL */}
							<div>
								<label htmlFor="target-url" className="block text-sm font-medium mb-2">
									Target Website
								</label>
								<input
									id="target-url"
									type="url"
									value={targetUrl}
									onChange={(e) => setTargetUrl(e.target.value)}
									readOnly
									className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-white cursor-not-allowed opacity-75"
									placeholder="https://example.com"
									disabled={status !== 'idle'}
								/>
								<p className="text-sm text-green-400 mt-2 flex items-center gap-2">
									<span>✓</span>
									<span>This website has AWI (Agent Web Interface) configured and ready</span>
								</p>
							</div>

							{/* Task */}
							<div>
								<label htmlFor="task" className="block text-sm font-medium mb-2">
									Task
								</label>
								<textarea
									id="task"
									value={task}
									onChange={(e) => setTask(e.target.value)}
									className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-white resize-none"
									rows={3}
									placeholder="Describe what the agent should do..."
									disabled={status !== 'idle'}
								/>
							</div>

							{/* API Key */}
							<div>
								<label htmlFor="api-key" className="block text-sm font-medium mb-2">
									OpenAI API Key
								</label>
								<input
									id="api-key"
									type="password"
									value={apiKey}
									onChange={(e) => setApiKey(e.target.value)}
									className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
									placeholder="sk-..."
									disabled={status !== 'idle'}
								/>
								<p className="text-xs text-gray-500 mt-1">
									Your API key is never stored. Used only for this execution.
								</p>
							</div>

							{/* AWI Registration Settings */}
							<div className="border-t border-gray-700 pt-4">
								<button
									onClick={() => setShowAwiConfig(!showAwiConfig)}
									className="flex items-center justify-between w-full text-sm font-medium text-gray-300 hover:text-white transition-colors"
									type="button"
								>
									<span>🤖 AWI Agent Registration</span>
									<span className="text-xs">{showAwiConfig ? '▼' : '▶'}</span>
								</button>

								{showAwiConfig && (
									<div className="mt-4 space-y-3">
										<div className="bg-blue-900/30 border border-blue-500/50 rounded p-3 text-xs text-blue-200">
											<p className="font-medium mb-1">ℹ️ Headless Registration</p>
											<p>These settings auto-register the agent without interactive prompts (required for server deployments).</p>
										</div>

										<div>
											<label htmlFor="awi-agent-name" className="block text-xs font-medium mb-2 text-gray-400">
												Agent Name
											</label>
											<input
												id="awi-agent-name"
												type="text"
												value={awiAgentName}
												onChange={(e) => setAwiAgentName(e.target.value)}
												className="w-full px-3 py-2 text-sm bg-gray-900 border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
												placeholder="BrowserUseAgent"
												disabled={status !== 'idle'}
											/>
										</div>

										<div>
											<label className="block text-xs font-medium mb-2 text-gray-400">
												Permissions
											</label>
											<div className="flex flex-wrap gap-2">
												{['read', 'write', 'delete'].map((perm) => (
													<label
														key={perm}
														className={`flex items-center gap-2 px-3 py-2 rounded cursor-pointer transition-colors ${
															awiPermissions.includes(perm)
																? 'bg-blue-600 text-white'
																: 'bg-gray-700 text-gray-300 hover:bg-gray-600'
														} ${status !== 'idle' ? 'opacity-50 cursor-not-allowed' : ''}`}
													>
														<input
															type="checkbox"
															checked={awiPermissions.includes(perm)}
															onChange={(e) => {
																if (e.target.checked) {
																	setAwiPermissions([...awiPermissions, perm])
																} else {
																	setAwiPermissions(awiPermissions.filter((p) => p !== perm))
																}
															}}
															disabled={status !== 'idle'}
															className="sr-only"
														/>
														<span className="text-sm capitalize">{perm}</span>
													</label>
												))}
											</div>
											<p className="text-xs text-gray-500 mt-2">
												Selected: {awiPermissions.length > 0 ? awiPermissions.join(', ') : 'none'}
											</p>
										</div>
									</div>
								)}
							</div>

							{/* Start/Stop Button */}
							<div className="flex gap-4">
								{(status === 'completed' || (status === 'error' && completionResult)) ? (
									<button
										onClick={() => {
											setStatus('idle')
											setLogs([])
											setCurrentStep(0)
											setCurrentAction('')
											setMetrics(null)
											setCompletionResult(null)
										}}
										className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
									>
										Start New Demo
									</button>
								) : (
									<>
										<button
											onClick={startDemo}
											disabled={status !== 'idle'}
											className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
										>
											{status === 'idle' ? 'Start Demo' : 'Running...'}
										</button>
										{status !== 'idle' && status !== 'error' && (
											<button
												onClick={stopDemo}
												className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 min-h-[44px]"
											>
												Stop
											</button>
										)}
									</>
								)}
							</div>
						</div>

						{/* Metrics */}
						{metrics && (
							<motion.div
								className="bg-gray-800 rounded-lg p-6 mt-6"
								initial={{ opacity: 0, y: 20 }}
								animate={{ opacity: 1, y: 0 }}
							>
								<div className="flex items-center justify-between mb-4">
									<h3 className="text-lg font-semibold">Execution Metrics</h3>
									{status === 'running' && (
										<span className="text-xs px-2 py-1 bg-blue-600 rounded">Live</span>
									)}
									{status === 'completed' && (
										<span className="text-xs px-2 py-1 bg-green-600 rounded">Completed</span>
									)}
									{status === 'error' && completionResult && (
										<span className="text-xs px-2 py-1 bg-orange-600 rounded">Partial</span>
									)}
								</div>
								<div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
									<div className="bg-gray-900 rounded p-4 text-center">
										<div className="text-2xl font-bold text-blue-400">
											{metrics.tokens.toLocaleString()}
										</div>
										<div className="text-sm text-gray-400">Total Tokens</div>
									</div>
									<div className="bg-gray-900 rounded p-4 text-center">
										<div className="text-2xl font-bold text-green-400">
											${metrics.cost > 0 ? metrics.cost.toFixed(4) : '0.0000'}
										</div>
										<div className="text-sm text-gray-400">Cost</div>
									</div>
									<div className="bg-gray-900 rounded p-4 text-center">
										<div className="text-2xl font-bold text-purple-400">{metrics.steps}</div>
										<div className="text-sm text-gray-400">Steps</div>
									</div>
									<div className="bg-gray-900 rounded p-4 text-center">
										<div className="text-2xl font-bold text-orange-400">
											{metrics.duration !== undefined
												? metrics.duration < 60
													? `${metrics.duration.toFixed(1)}s`
													: `${Math.floor(metrics.duration / 60)}m ${(metrics.duration % 60).toFixed(0)}s`
												: '-'}
										</div>
										<div className="text-sm text-gray-400">Duration</div>
									</div>
								</div>
								{/* Token breakdown */}
								{(metrics.prompt_tokens !== undefined || metrics.completion_tokens !== undefined) && (
									<div className="grid grid-cols-2 gap-4">
										<div className="bg-gray-900/50 rounded p-3 text-center">
											<div className="text-lg font-semibold text-yellow-400">
												{(metrics.prompt_tokens || 0).toLocaleString()}
											</div>
											<div className="text-xs text-gray-400">Input Tokens</div>
										</div>
										<div className="bg-gray-900/50 rounded p-3 text-center">
											<div className="text-lg font-semibold text-green-400">
												{(metrics.completion_tokens || 0).toLocaleString()}
											</div>
											<div className="text-xs text-gray-400">Output Tokens</div>
										</div>
									</div>
								)}
							</motion.div>
						)}
					</motion.div>

					{/* Right: Execution Log */}
					<motion.div
						initial={{ opacity: 0, x: 20 }}
						animate={{ opacity: 1, x: 0 }}
						transition={{ duration: 0.5 }}
					>
						<div className="bg-gray-800 rounded-lg p-6">
							<div className="mb-4">
								<h2 className="text-xl font-semibold">Execution Log</h2>
								{status === 'running' && currentAction && (
									<div className="mt-2 text-sm text-gray-400 italic">
										Current action: {currentAction}
									</div>
								)}
							</div>

							{/* Completion Banner */}
							{(status === 'completed' || (status === 'error' && completionResult)) && completionResult && (
								<motion.div
									initial={{ opacity: 0, y: -10 }}
									animate={{ opacity: 1, y: 0 }}
									className={`mb-4 p-4 rounded-lg border-2 ${
										completionResult.success
											? 'bg-green-900/30 border-green-500 text-green-100'
											: completionResult.result === 'Execution stopped by user'
												? 'bg-orange-900/30 border-orange-500 text-orange-100'
												: 'bg-red-900/30 border-red-500 text-red-100'
									}`}
								>
									<div className="flex items-start gap-3">
										<div className="text-2xl">
											{completionResult.success ? '✅' : completionResult.result === 'Execution stopped by user' ? '⏸️' : '❌'}
										</div>
										<div className="flex-1">
											<h3 className="font-semibold text-lg mb-2">
												{completionResult.success
													? 'Execution Completed Successfully'
													: completionResult.result === 'Execution stopped by user'
														? 'Execution Stopped'
														: 'Execution Failed'}
											</h3>
											{completionResult.result && completionResult.result !== 'Execution stopped by user' && (
												<div className="text-sm space-y-1">
													<p className="font-medium">Final Result:</p>
													<p className="whitespace-pre-wrap bg-black/20 p-3 rounded">
														{completionResult.result}
													</p>
												</div>
											)}
											<p className="text-sm mt-2 opacity-80">
												{completionResult.success ? 'Completed' : 'Stopped'} after {completionResult.totalSteps} steps
											</p>
										</div>
									</div>
								</motion.div>
							)}

							{/* Log Display */}
							<div className="bg-gray-900 rounded p-4 h-[600px] overflow-y-auto font-mono text-sm">
								{logs.length === 0 ? (
									<div className="text-gray-500 text-center py-20">
										Configure settings and click &quot;Start Demo&quot; to begin
									</div>
								) : (
									<div className="space-y-2">
										{logs.map((log, index) => (
											<div
												key={index}
												className={`${
													log.type === 'error'
														? 'text-red-400'
														: log.type === 'success'
															? 'text-green-400'
															: log.type === 'step'
																? 'text-blue-400'
																: 'text-gray-300'
												}`}
											>
												<span className="text-gray-600">
													[{new Date(log.timestamp).toLocaleTimeString()}]
												</span>{' '}
												{log.message}
											</div>
										))}
									</div>
								)}
							</div>
						</div>
					</motion.div>
				</div>
			</div>
		</main>
	)
}
