/**
 * WebSocket client for live demo execution
 */

export interface LiveDemoMessage {
	type: 'ready' | 'status' | 'agent_started' | 'step' | 'completed' | 'metrics' | 'error' | 'log' | 'agent_registry'
	message?: string
	task?: string
	step_number?: number
	action?: string
	timestamp?: number
	success?: boolean
	total_steps?: number
	result?: any
	tokens?: number
	prompt_tokens?: number
	completion_tokens?: number
	steps?: number
	cost?: number
	mode?: string
	level?: string  // Log level: INFO, WARNING, ERROR, DEBUG
	agents?: Array<{
		agent_id: string
		agent_name: string
		domain: string
		awi_name: string
		permissions: string[]
		created_at: string
		last_used: string | null
	}>
	cli_command?: string
}

export class LiveDemoClient {
	private ws: WebSocket | null = null
	private sessionId: string
	private apiUrl: string
	private wsUrl: string

	constructor(sessionId: string, apiUrl: string = 'http://localhost:8000') {
		this.sessionId = sessionId
		this.apiUrl = apiUrl
		this.wsUrl = apiUrl.replace('http', 'ws')
	}

	connect(onMessage: (message: LiveDemoMessage) => void, onError?: (error: Event) => void): Promise<void> {
		return new Promise((resolve, reject) => {
			const wsEndpoint = `${this.wsUrl}/api/live/ws/live/${this.sessionId}`

			try {
				this.ws = new WebSocket(wsEndpoint)

				this.ws.onopen = () => {
					console.log('[WebSocket] Connected')
					resolve()
				}

				this.ws.onmessage = (event) => {
					try {
						const data = JSON.parse(event.data) as LiveDemoMessage
						onMessage(data)
					} catch (error) {
						console.error('[WebSocket] Failed to parse message:', error)
					}
				}

				this.ws.onerror = (error) => {
					console.error('[WebSocket] Error:', error)
					if (onError) {
						onError(error)
					}
					reject(error)
				}

				this.ws.onclose = () => {
					console.log('[WebSocket] Connection closed')
				}
			} catch (error) {
				console.error('[WebSocket] Failed to connect:', error)
				reject(error)
			}
		})
	}

	sendApiKey(apiKey: string) {
		if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
			throw new Error('WebSocket not connected')
		}

		this.ws.send(
			JSON.stringify({
				api_key: apiKey,
			})
		)
	}

	disconnect() {
		if (this.ws) {
			this.ws.close()
			this.ws = null
		}
	}

	isConnected(): boolean {
		return this.ws !== null && this.ws.readyState === WebSocket.OPEN
	}
}
