/**
 * API client utilities for browser-use demo
 */

/**
 * Get the API URL from environment or default
 */
export function getApiUrl(): string {
	return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}

/**
 * Check if backend is reachable
 */
export async function checkBackendHealth(apiUrl?: string): Promise<{
	reachable: boolean
	error?: string
	latency?: number
}> {
	const backendUrl = apiUrl || getApiUrl()
	const startTime = Date.now()

	try {
		const controller = new AbortController()
		const timeoutId = setTimeout(() => controller.abort(), 10000) // 10s timeout

		const response = await fetch(`${backendUrl}/health`, {
			method: 'GET',
			signal: controller.signal,
		})

		clearTimeout(timeoutId)
		const latency = Date.now() - startTime

		if (!response.ok) {
			return {
				reachable: false,
				error: `Backend returned ${response.status}: ${response.statusText}`,
				latency,
			}
		}

		return {
			reachable: true,
			latency,
		}
	} catch (error) {
		const latency = Date.now() - startTime

		if (error instanceof Error) {
			// Specific error messages
			if (error.name === 'AbortError') {
				return {
					reachable: false,
					error: 'Backend timeout (10s). Server may be sleeping or unreachable.',
					latency,
				}
			}

			if (error.message.includes('Failed to fetch')) {
				return {
					reachable: false,
					error: 'Cannot connect to backend. Check CORS, network, or if backend is running.',
					latency,
				}
			}

			return {
				reachable: false,
				error: error.message,
				latency,
			}
		}

		return {
			reachable: false,
			error: 'Unknown error connecting to backend',
			latency,
		}
	}
}

/**
 * Start a live demo session
 */
export async function startLiveDemo(params: {
	task: string
	mode: 'awi' | 'permission' | 'traditional'
	targetUrl: string
	apiKey: string
	backendUrl?: string
}): Promise<{
	success: boolean
	sessionId?: string
	error?: string
}> {
	const apiUrl = params.backendUrl || getApiUrl()

	try {
		const response = await fetch(`${apiUrl}/api/live/start`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				task: params.task,
				mode: params.mode,
				target_url: params.targetUrl,
				api_key: params.apiKey,
			}),
		})

		if (!response.ok) {
			const errorText = await response.text()
			return {
				success: false,
				error: `Backend error (${response.status}): ${errorText}`,
			}
		}

		const data = await response.json()
		return {
			success: true,
			sessionId: data.session_id,
		}
	} catch (error) {
		if (error instanceof Error) {
			if (error.message.includes('Failed to fetch')) {
				return {
					success: false,
					error: 'Cannot connect to backend. CORS or network issue. Check browser console for details.',
				}
			}

			return {
				success: false,
				error: error.message,
			}
		}

		return {
			success: false,
			error: 'Unknown error starting demo',
		}
	}
}

/**
 * Get diagnostic information for troubleshooting
 */
export function getDiagnosticInfo() {
	const apiUrl = getApiUrl()

	return {
		apiUrl,
		isLocalhost: apiUrl.includes('localhost') || apiUrl.includes('127.0.0.1'),
		protocol: apiUrl.startsWith('https') ? 'HTTPS' : 'HTTP',
		currentOrigin: typeof window !== 'undefined' ? window.location.origin : 'unknown',
		userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
	}
}
