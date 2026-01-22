'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'

export default function Home() {
	return (
		<main className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white" role="main">
			{/* Skip to main content link for screen readers */}
			<a
				href="#main-content"
				className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded"
			>
				Skip to main content
			</a>
			<div id="main-content" className="container mx-auto px-4 py-16">
				{/* Hero Section */}
				<motion.div
					className="text-center mb-16"
					initial={{ opacity: 0, y: 20 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ duration: 0.8 }}
				>
					<motion.h1
						className="text-6xl font-bold mb-4"
						initial={{ opacity: 0, y: -20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.2, duration: 0.8 }}
					>
						AI Browser Automation
					</motion.h1>
					<motion.p
						className="text-3xl font-semibold text-blue-400 mb-6"
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						transition={{ delay: 0.4, duration: 0.8 }}
					>
						10x More Efficient Than Traditional Scraping
					</motion.p>
					<motion.p
						className="text-xl text-gray-300 max-w-3xl mx-auto mb-8"
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						transition={{ delay: 0.6, duration: 0.8 }}
					>
						Experience the power of browser-use with three execution modes: Traditional DOM parsing,
						Permission-based security, and revolutionary AWI mode with structured APIs.
					</motion.p>
					<motion.div
						className="flex justify-center gap-4 flex-wrap"
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.8, duration: 0.8 }}
					>
						<Link
							href="/showcase"
							className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
						>
							View Demos
						</Link>
						<Link
							href="/live"
							className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
						>
							Try Live Demo
						</Link>
						<a
							href="https://github.com/starks-and-wolves/ai-browser-secure"
							target="_blank"
							rel="noopener noreferrer"
							className="bg-gray-700 hover:bg-gray-600 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
						>
							GitHub
						</a>
					</motion.div>
				</motion.div>

				{/* Key Metrics */}
				<motion.div
					className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-16"
					initial={{ opacity: 0 }}
					animate={{ opacity: 1 }}
					transition={{ delay: 1.0, duration: 0.8 }}
					role="region"
					aria-label="Key performance metrics"
				>
					<motion.div
						className="bg-gray-800 rounded-lg p-6 text-center"
						initial={{ opacity: 0, scale: 0.8 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ delay: 1.2, duration: 0.5 }}
						whileHover={{ scale: 1.05 }}
						role="article"
						aria-label="Token reduction metric"
					>
						<div className="text-5xl font-bold text-blue-400 mb-2" aria-label="95 percent">
							95%
						</div>
						<div className="text-xl mb-1">Token Reduction</div>
						<div className="text-gray-400 text-sm">10K → 500 tokens</div>
					</motion.div>
					<motion.div
						className="bg-gray-800 rounded-lg p-6 text-center"
						initial={{ opacity: 0, scale: 0.8 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ delay: 1.4, duration: 0.5 }}
						whileHover={{ scale: 1.05 }}
						role="article"
						aria-label="Cost per task metric"
					>
						<div className="text-5xl font-bold text-green-400 mb-2" aria-label="0.01 dollars">
							$0.01
						</div>
						<div className="text-xl mb-1">Cost per Task</div>
						<div className="text-gray-400 text-sm">vs $0.10 traditional</div>
					</motion.div>
					<motion.div
						className="bg-gray-800 rounded-lg p-6 text-center"
						initial={{ opacity: 0, scale: 0.8 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ delay: 1.6, duration: 0.5 }}
						whileHover={{ scale: 1.05 }}
						role="article"
						aria-label="Speed improvement metric"
					>
						<div className="text-5xl font-bold text-purple-400 mb-2" aria-label="5 times faster">
							5x
						</div>
						<div className="text-xl mb-1">Speed Improvement</div>
						<div className="text-gray-400 text-sm">3s vs 15s</div>
					</motion.div>
				</motion.div>

				{/* Mode Comparison Table */}
				<motion.div
					className="max-w-6xl mx-auto"
					initial={{ opacity: 0, y: 40 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ delay: 1.8, duration: 0.8 }}
				>
					<h2 className="text-4xl font-bold text-center mb-8">Three Execution Modes</h2>
					<div className="bg-gray-800 rounded-lg overflow-hidden">
						<table className="w-full">
							<thead className="bg-gray-700">
								<tr>
									<th className="px-6 py-4 text-left">Metric</th>
									<th className="px-6 py-4 text-center">Traditional</th>
									<th className="px-6 py-4 text-center">Permission</th>
									<th className="px-6 py-4 text-center">AWI Mode</th>
								</tr>
							</thead>
							<tbody className="divide-y divide-gray-700">
								<tr>
									<td className="px-6 py-4 font-semibold">Token Usage</td>
									<td className="px-6 py-4 text-center">10,000 🪙</td>
									<td className="px-6 py-4 text-center">8,000 🪙</td>
									<td className="px-6 py-4 text-center text-green-400">500 🪙</td>
								</tr>
								<tr>
									<td className="px-6 py-4 font-semibold">Cost/Task</td>
									<td className="px-6 py-4 text-center">$0.10</td>
									<td className="px-6 py-4 text-center">$0.08</td>
									<td className="px-6 py-4 text-center text-green-400">$0.01</td>
								</tr>
								<tr>
									<td className="px-6 py-4 font-semibold">Speed</td>
									<td className="px-6 py-4 text-center">15s</td>
									<td className="px-6 py-4 text-center">12s</td>
									<td className="px-6 py-4 text-center text-green-400">3s</td>
								</tr>
								<tr>
									<td className="px-6 py-4 font-semibold">Security</td>
									<td className="px-6 py-4 text-center">⚠️ Basic</td>
									<td className="px-6 py-4 text-center">✅ Strong</td>
									<td className="px-6 py-4 text-center">✅ API-level</td>
								</tr>
								<tr>
									<td className="px-6 py-4 font-semibold">Data Access</td>
									<td className="px-6 py-4 text-center">Full DOM</td>
									<td className="px-6 py-4 text-center">User-approved</td>
									<td className="px-6 py-4 text-center">Structured</td>
								</tr>
							</tbody>
						</table>
					</div>
				</motion.div>

				{/* What is AWI Section */}
				<motion.div
					className="max-w-6xl mx-auto mt-16"
					initial={{ opacity: 0, y: 40 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ delay: 2.0, duration: 0.8 }}
				>
					<h2 className="text-4xl font-bold text-center mb-8">What is AWI (Agent Web Interface)?</h2>
					<div className="bg-gray-800 rounded-lg p-8 space-y-6">
						<p className="text-lg text-gray-300">
							<strong className="text-blue-400">AWI (Agent Web Interface)</strong> is a revolutionary approach to web automation that provides structured APIs instead of requiring DOM parsing. Unlike traditional browser automation that scrapes HTML and executes JavaScript, AWI exposes clean, agent-friendly endpoints.
						</p>

						<div className="grid md:grid-cols-2 gap-6 mt-6">
							<div className="bg-gray-900 rounded-lg p-6">
								<h3 className="text-xl font-semibold text-green-400 mb-3">✅ AWI Benefits</h3>
								<ul className="space-y-2 text-gray-300">
									<li>• <strong>No DOM Parsing:</strong> Direct API access eliminates HTML parsing overhead</li>
									<li>• <strong>Efficient for Heavy Sites:</strong> Bypasses expensive JavaScript execution on content-rich websites</li>
									<li>• <strong>Token Reduction:</strong> Structured responses use 95% fewer tokens than full DOM trees</li>
									<li>• <strong>Reliability:</strong> APIs are more stable than fragile CSS selectors</li>
									<li>• <strong>Server-Side State:</strong> Backend maintains session context and history</li>
								</ul>
							</div>

							<div className="bg-gray-900 rounded-lg p-6">
								<h3 className="text-xl font-semibold text-purple-400 mb-3">🎯 When to Use AWI</h3>
								<ul className="space-y-2 text-gray-300">
									<li>• <strong>JavaScript-Heavy Sites:</strong> Modern SPAs with complex rendering</li>
									<li>• <strong>Content Platforms:</strong> Blogs, e-commerce, social media</li>
									<li>• <strong>Repeated Operations:</strong> Tasks that benefit from session state</li>
									<li>• <strong>Cost-Sensitive Apps:</strong> High-volume automation with budget constraints</li>
								</ul>
							</div>
						</div>

						<div className="bg-blue-900/30 border border-blue-500/50 rounded-lg p-6 mt-6">
							<h4 className="text-lg font-semibold text-blue-300 mb-2">Technical Overview</h4>
							<p className="text-gray-300">
								AWI works by having websites expose a <code className="bg-gray-700 px-2 py-1 rounded">.well-known/llm-text</code> manifest that describes available operations, authentication, and endpoints. AI agents discover this manifest, register with permissions, and make structured API calls instead of navigating through the DOM. This reduces token usage by 20x and execution time by 5x compared to traditional scraping.
							</p>
						</div>

						<div className="bg-purple-900/30 border border-purple-500/50 rounded-lg p-6 mt-6">
							<h4 className="text-lg font-semibold text-purple-300 mb-2">State Management & Redis</h4>
							<p className="text-gray-300">
								State management is critical in AWI because it enables agents to maintain context across multiple API calls, track pagination progress, remember user preferences, and preserve session data without re-sending full context to the LLM. Redis serves as an ideal state store for AWI implementations, providing fast in-memory access for session tracking, real-time state synchronization across distributed agents, and automatic expiration for temporary data. By offloading state to Redis, AWI backends can return minimal deltas instead of complete application state, further reducing token consumption and enabling stateful multi-step workflows that would be prohibitively expensive with traditional DOM-based approaches.
							</p>
						</div>
					</div>
				</motion.div>

				{/* Security & Permission Violations Section */}
				<motion.div
					className="max-w-6xl mx-auto mt-16"
					initial={{ opacity: 0, y: 40 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ delay: 2.2, duration: 0.8 }}
				>
					<h2 className="text-4xl font-bold text-center mb-8">Security & Permission Control</h2>
					<div className="bg-gray-800 rounded-lg p-8">
						<div className="mb-8">
							<h3 className="text-2xl font-semibold text-orange-400 mb-4">Why Permission Mode Matters</h3>
							<p className="text-lg text-gray-300 mb-4">
								Recent incidents have highlighted the critical need for explicit permission controls in AI agent automation:
							</p>
						</div>

						<div className="space-y-6">
							<div className="bg-red-900/30 border border-red-500/50 rounded-lg p-6">
								<h4 className="text-xl font-semibold text-red-300 mb-3">🚨 Unseeable Prompt Injections - Comet and other AI browsers</h4>
								<p className="text-gray-300 mb-3">
									Brave's research revealed how AI browsers like Comet are vulnerable to invisible prompt injection attacks. Malicious actors can embed hidden instructions in web pages that manipulate AI agents into performing unauthorized actions, bypassing security controls without user awareness.
								</p>
								<a
									href="https://brave.com/blog/unseeable-prompt-injections/"
									target="_blank"
									rel="noopener noreferrer"
									className="text-blue-400 hover:text-blue-300 underline text-sm"
								>
									Read: Unseeable Prompt Injections (Brave) →
								</a>
							</div>

							<div className="bg-red-900/30 border border-red-500/50 rounded-lg p-6">
								<h4 className="text-xl font-semibold text-red-300 mb-3">🛡️ Brave's AI Agent Security Research (2024)</h4>
								<p className="text-gray-300 mb-3">
									Brave Browser's research highlighted how AI agents can be exploited to access sensitive data without user consent. Their findings emphasized the need for explicit permission systems and domain controls to prevent unauthorized data exfiltration.
								</p>
								<a
									href="https://brave.com/blog/securing-web-agents/"
									target="_blank"
									rel="noopener noreferrer"
									className="text-blue-400 hover:text-blue-300 underline text-sm"
								>
									Read: Securing the AI Agent Ecosystem (Brave) →
								</a>
							</div>

							<div className="bg-gray-900 rounded-lg p-6">
								<h4 className="text-xl font-semibold text-green-400 mb-3">✅ Our Solution: Permission Mode</h4>
								<p className="text-gray-300 mb-4">
									Browser-use's Permission Mode addresses these concerns with:
								</p>
								<ul className="space-y-2 text-gray-300 list-disc list-inside">
									<li>Explicit user approval for all navigation and form submissions</li>
									<li>Domain whitelisting and blacklisting for fine-grained access control</li>
									<li>Sensitive data masking in execution history</li>
									<li>Pre-approved domain lists for trusted sites</li>
									<li>Automatic blocking of prohibited domains</li>
								</ul>
							</div>
						</div>

						<div className="bg-purple-900/30 border border-purple-500/50 rounded-lg p-6 mt-6">
							<h4 className="text-xl font-semibold text-purple-300 mb-3">📚 OWASP GenAI Security Guidelines</h4>
							<p className="text-gray-300 mb-3">
								Our security approach aligns with OWASP's Top 10 for LLM Applications and Generative AI Security, addressing risks like prompt injection, data leakage, and unauthorized access.
							</p>
							<div className="flex flex-wrap gap-4 mt-4">
								<a
									href="https://owasp.org/www-project-top-10-for-large-language-model-applications/"
									target="_blank"
									rel="noopener noreferrer"
									className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors text-sm"
								>
									OWASP Top 10 for LLMs →
								</a>
								<a
									href="https://genai.owasp.org/"
									target="_blank"
									rel="noopener noreferrer"
									className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors text-sm"
								>
									OWASP GenAI Security →
								</a>
							</div>
						</div>
					</div>
				</motion.div>

				{/* Footer */}
				<div className="mt-16 border-t border-gray-700 pt-8">
					<div className="max-w-4xl mx-auto">
						<div className="grid md:grid-cols-2 gap-8 mb-8">
							<div>
								<h3 className="text-lg font-semibold mb-3">Research & Documentation</h3>
								<ul className="space-y-2 text-gray-400">
									<li>
										<a
											href="https://github.com/browser-use/browser-use"
											target="_blank"
											rel="noopener noreferrer"
											className="hover:text-blue-400 transition-colors"
										>
											→ Browser-Use GitHub Repository
										</a>
									</li>
									<li>
										<a
											href="https://arxiv.org/abs/2506.10953"
											target="_blank"
											rel="noopener noreferrer"
											className="hover:text-blue-400 transition-colors"
										>
											→ Build the web for agents, not agents for the web (Research Paper)
										</a>
									</li>
									<li>
										<a
											href="https://docs.browser-use.com/"
											target="_blank"
											rel="noopener noreferrer"
											className="hover:text-blue-400 transition-colors"
										>
											→ Official Documentation
										</a>
									</li>
								</ul>
							</div>
							<div>
								<h3 className="text-lg font-semibold mb-3">Security Resources</h3>
								<ul className="space-y-2 text-gray-400">
									<li>
										<a
											href="https://owasp.org/www-project-top-10-for-large-language-model-applications/"
											target="_blank"
											rel="noopener noreferrer"
											className="hover:text-blue-400 transition-colors"
										>
											→ OWASP Top 10 for LLMs
										</a>
									</li>
									<li>
										<a
											href="https://genai.owasp.org/"
											target="_blank"
											rel="noopener noreferrer"
											className="hover:text-blue-400 transition-colors"
										>
											→ OWASP GenAI Security
										</a>
									</li>
									<li>
										<a
											href="https://www.anthropic.com/research/building-effective-agents"
											target="_blank"
											rel="noopener noreferrer"
											className="hover:text-blue-400 transition-colors"
										>
											→ Anthropic: Building Effective Agents
										</a>
									</li>
								</ul>
							</div>
						</div>
						<div className="text-center text-gray-400 border-t border-gray-700 pt-6">
							<p className="mb-2">Built with browser-use | Open Source</p>
							<p className="text-sm text-gray-500">
								Demo application showcasing AWI mode, Permission controls, and Traditional browser automation
							</p>
						</div>
					</div>
				</div>
			</div>
		</main>
	)
}
