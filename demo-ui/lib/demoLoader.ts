import type {
	AgentHistory,
	AgentHistoryList,
	DemoMetadata,
	DemoStep,
	DemoManifest,
} from './types'

/**
 * Format an action object into a human-readable string
 */
export function formatAction(actionName: string, actionParams: any): string {
	switch (actionName) {
		case 'go_to_url':
			return `Navigate to ${actionParams.url}`
		case 'click_element':
			return `Click element at index ${actionParams.index}`
		case 'input_text':
			return `Type "${actionParams.text}" into element ${actionParams.index}`
		case 'scroll':
			return `Scroll ${actionParams.direction || 'down'}`
		case 'extract_content':
			return `Extract content from page`
		case 'done':
			return `Task completed: ${actionParams.text || ''}`
		case 'awi_execute':
			return `AWI: ${actionParams.method} ${actionParams.endpoint}`
		default:
			return `${actionName}: ${JSON.stringify(actionParams).substring(0, 50)}`
	}
}

/**
 * Estimate token count for a model output (rough approximation)
 */
export function estimateTokens(modelOutput: any): number {
	const text = JSON.stringify(modelOutput)
	// Rough estimate: 1 token ≈ 4 characters
	return Math.ceil(text.length / 4)
}

/**
 * Process AgentHistory JSON into displayable steps
 */
export function processAgentHistory(json: AgentHistoryList): DemoStep[] {
	return json.history.map((item, idx) => {
		const action = item.model_output?.action[0] || {}
		const actionName = Object.keys(action)[0] || 'unknown'
		const actionParams = action[actionName] || {}

		return {
			stepNumber: idx + 1,
			action: formatAction(actionName, actionParams),
			actionDetails: action,
			result: item.result[0]?.extracted_content || 'N/A',
			screenshot: item.state.screenshot_path || undefined,
			duration:
				item.metadata?.step_end_time && item.metadata?.step_start_time
					? item.metadata.step_end_time - item.metadata.step_start_time
					: 0,
			tokensUsed: item.model_output ? estimateTokens(item.model_output) : 0,
		}
	})
}

/**
 * Calculate total metrics from processed steps
 */
export function calculateMetrics(steps: DemoStep[]) {
	const totalTokens = steps.reduce((sum, step) => sum + (step.tokensUsed || 0), 0)
	const totalDuration = steps.reduce((sum, step) => sum + step.duration, 0)
	const totalSteps = steps.length

	// Rough cost estimate (assumes GPT-4 pricing: ~$0.01/1K tokens)
	const estimatedCost = (totalTokens / 1000) * 0.01

	return {
		steps: totalSteps,
		tokens: totalTokens,
		duration: totalDuration,
		cost: estimatedCost,
	}
}

/**
 * Load demo manifest from public/demos/index.json
 */
export async function loadDemoManifest(): Promise<DemoManifest> {
	const response = await fetch('/demos/index.json')
	if (!response.ok) {
		throw new Error(`Failed to load demo manifest: ${response.statusText}`)
	}
	return response.json()
}

/**
 * Load a specific demo trajectory by ID
 */
export async function loadDemo(demoId: string): Promise<AgentHistoryList> {
	const response = await fetch(`/demos/${demoId}.json`)
	if (!response.ok) {
		throw new Error(`Failed to load demo ${demoId}: ${response.statusText}`)
	}
	return response.json()
}

/**
 * Load and process a demo into displayable steps
 */
export async function loadAndProcessDemo(demoId: string): Promise<DemoStep[]> {
	const trajectory = await loadDemo(demoId)
	return processAgentHistory(trajectory)
}
