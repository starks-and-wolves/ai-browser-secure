/**
 * TypeScript types mirroring Python Pydantic models from browser_use/agent/views.py
 * These types represent the AgentHistory trajectory format
 */

// ActionResult - Result of executing an action
export interface ActionResult {
	// For done action
	is_done?: boolean
	success?: boolean | null

	// For trace judgement
	judgement?: JudgementResult | null

	// Error handling
	error?: string | null

	// Files
	attachments?: string[] | null

	// Images (base64 encoded)
	images?: Array<{ name: string; data: string }> | null

	// Always include in long term memory
	long_term_memory?: string | null

	// Extracted content
	extracted_content?: string | null
	include_extracted_content_only_once?: boolean

	// Metadata for observability
	metadata?: Record<string, any> | null

	// Deprecated
	include_in_memory?: boolean
}

// JudgementResult - LLM judgement of agent trace
export interface JudgementResult {
	reasoning?: string | null
	verdict: boolean
	failure_reason?: string | null
	impossible_task?: boolean
	reached_captcha?: boolean
}

// ActionModel - Represents a single action (simplified)
export type ActionModel = Record<string, any>

// AgentOutput - Model output from the LLM
export interface AgentOutput {
	thinking?: string | null
	evaluation_previous_goal?: string | null
	memory?: string | null
	next_goal?: string | null
	action: ActionModel[] // List of actions to execute
}

// StepMetadata - Metadata for a single step
export interface StepMetadata {
	step_start_time: number
	step_end_time: number
	step_number: number
	step_interval?: number | null
}

// BrowserStateHistory - State of the browser at a specific point
export interface BrowserStateHistory {
	url?: string
	title?: string
	tabs?: TabInfo[]
	screenshot_path?: string | null
	interacted_element?: DOMInteractedElement[]
	selector_map?: Record<number, any>
	page_info?: PageInfo | null
}

// TabInfo - Information about a browser tab
export interface TabInfo {
	url: string
	title: string
	target_id: string
	parent_target_id?: string | null
}

// PageInfo - Viewport and scroll information
export interface PageInfo {
	width: number
	height: number
	device_pixel_ratio: number
	scroll_x: number
	scroll_y: number
	visible_width: number
	visible_height: number
}

// DOMInteractedElement - DOM element that was interacted with
export interface DOMInteractedElement {
	tag_name: string
	xpath: string
	attributes?: Record<string, string>
	text_content?: string | null
}

// AgentHistory - History item for agent actions
export interface AgentHistory {
	model_output: AgentOutput | null
	result: ActionResult[]
	state: BrowserStateHistory
	metadata?: StepMetadata | null
	state_message?: string | null
}

// AgentHistoryList - Complete agent execution history
export interface AgentHistoryList {
	history: AgentHistory[]
	final_result?: any | null
	errors?: string[]
}

// Demo metadata for the UI
export interface DemoMetadata {
	id: string
	title: string
	description: string
	mode: 'traditional' | 'permission' | 'awi'
	task: string
	metrics: {
		steps: number
		tokens: number
		cost: number
		duration: number
	}
	thumbnail?: string
	trajectory_url: string
	video_url?: string
}

// Processed step for display in the UI
export interface DemoStep {
	stepNumber: number
	action: string // Formatted action description
	actionDetails: ActionModel // Raw action data
	result: string // Result summary
	screenshot?: string // Screenshot URL or base64
	duration: number // Duration in seconds
	tokensUsed?: number // Estimated tokens
}

// Demo manifest index
export interface DemoManifest {
	demos: DemoMetadata[]
}
