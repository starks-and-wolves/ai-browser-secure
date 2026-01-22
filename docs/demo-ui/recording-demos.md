# Recording Demos Guide

This guide explains how to record new browser-use demonstrations for the demo UI.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Recording Script Usage](#recording-script-usage)
3. [Demo Best Practices](#demo-best-practices)
4. [Processing Demos](#processing-demos)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Record a single demo
python browser_use/scripts/record_demo.py \
  --task "Find top 5 posts about browser automation on r/programming" \
  --output ./demos/reddit-search-traditional \
  --mode traditional \
  --max-steps 30

# Record all demos (traditional + AWI + permission)
bash browser_use/scripts/record_all_demos.sh

# Generate manifest for demo UI
python browser_use/scripts/generate_manifest.py --demos-dir ./demos
```

---

## Recording Script Usage

### Basic Command

```bash
python browser_use/scripts/record_demo.py \
  --task "Your task description here" \
  --output /path/to/output/directory \
  --mode [traditional|awi|permission] \
  --max-steps 30
```

### Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `--task` | Yes | Natural language task description | - |
| `--output` | Yes | Output directory for trajectory and screenshots | - |
| `--mode` | No | Execution mode: `traditional`, `awi`, or `permission` | `traditional` |
| `--max-steps` | No | Maximum agent steps before timeout | `30` |
| `--headless` | No | Run browser in headless mode | `False` |
| `--llm-provider` | No | LLM provider: `openai`, `anthropic`, `google` | `openai` |
| `--model` | No | Model name (e.g., `gpt-4o`, `claude-sonnet-4-5`) | Provider default |

### Examples

**Traditional Mode (DOM Parsing) - WITH VIDEO:**
```bash
python browser_use/scripts/record_demo.py \
  --task "Search for 'browser-use' on GitHub and find the repository" \
  --output ./demos/github-search-traditional \
  --mode traditional \
  --max-steps 20
# Video will be saved to: ./demos/github-search-traditional/videos/recording.webm
# This creates a visual recording showing browser navigation
```

**Note**: Video recording works best in **headed mode** (without --headless flag). This allows you to see the browser window during recording and results in better quality videos.

**AWI Mode (Structured API):**
```bash
python browser_use/scripts/record_demo.py \
  --task "Find top 5 posts about AI on r/MachineLearning" \
  --output ./demos/reddit-awi \
  --mode awi \
  --max-steps 10
```

**Permission Mode (Security-focused):**
```bash
python browser_use/scripts/record_demo.py \
  --task "Compare prices for MacBook Pro on Amazon and BestBuy" \
  --output ./demos/ecommerce-permission \
  --mode permission \
  --max-steps 25
```

**Custom Model:**
```bash
python browser_use/scripts/record_demo.py \
  --task "Summarize latest news on TechCrunch" \
  --output ./demos/news-summary \
  --llm-provider anthropic \
  --model claude-sonnet-4-5 \
  --max-steps 15
```

### Environment Variables

Set up API keys before recording:

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Google
export GOOGLE_API_KEY=...
```

---

## Demo Best Practices

### Choosing Tasks

**Good Tasks:**
- Clear, specific goals (e.g., "Find top 5 posts about X")
- 5-15 steps for traditional mode
- 2-5 API calls for AWI mode
- Showcase key features (navigation, data extraction, form filling)

**Avoid:**
- Vague tasks (e.g., "Browse the web")
- Time-sensitive content (today's news, current weather)
- Tasks requiring authentication (unless demonstrating that feature)
- Very long tasks (>30 steps) - they're hard to showcase

### Task Ideas by Mode

**Traditional Mode (DOM Parsing):**
- Reddit post search
- GitHub repository search
- Product price comparison
- News article summarization
- Wikipedia research

**AWI Mode (Structured API):**
- Reddit API: list posts, search, get comments
- HackerNews API: top stories, best comments
- Any site with AWI manifest support

**Permission Mode (Security):**
- E-commerce with tracker blocking
- Form filling with sensitive data
- Multi-domain navigation with approval prompts

### Recording Tips

1. **Test Task First**
   - Run the agent manually to verify task is achievable
   - Estimate steps needed (add 20% buffer)

2. **Use Descriptive Titles**
   ```bash
   # Good
   --output ./demos/reddit-search-browser-automation

   # Bad
   --output ./demos/demo1
   ```

3. **Watch for Errors**
   - Monitor console output during recording
   - Check for navigation failures or timeouts
   - Re-record if agent gets stuck

4. **Verify Output**
   ```bash
   # Check trajectory file exists
   ls demos/your-demo/trajectory.json

   # Check final result is successful
   cat demos/your-demo/trajectory.json | jq '.final_result.is_done'
   # Should return: true
   ```

---

## Processing Demos

### Output Structure

After recording, each demo directory contains:

```
demos/reddit-search-traditional/
├── trajectory.json          # Full agent history (AgentHistory format)
├── metadata.json            # Demo metadata (title, metrics, etc.)
├── videos/                  # Video recording (automatically generated)
│   └── recording.webm       # Browser navigation video
└── screenshots/             # (Optional) Step screenshots
    ├── step_1.png
    ├── step_2.png
    └── ...
```

**Video Recording**:
- Videos are automatically recorded when using the record_demo.py script
- Format: WebM (2 FPS by default for smaller file size)
- Location: `{output_dir}/videos/recording.webm`
- Shows actual browser navigation during execution
- **Best for Traditional mode** - visually shows DOM parsing and navigation
- AWI/Permission modes typically don't need video (fewer visual steps)

### Generate Manifest

The manifest file (`public/demos/index.json`) lists all demos for the UI:

```bash
python browser_use/scripts/generate_manifest.py \
  --demos-dir ./demos \
  --output ./demo-ui/public/demos/index.json
```

**Manifest Format:**
```json
{
  "demos": [
    {
      "id": "reddit-search-traditional",
      "title": "Reddit Search - Traditional Mode",
      "description": "Find posts about browser automation using DOM parsing",
      "mode": "traditional",
      "task": "Find top 5 posts about 'browser automation' on r/programming",
      "metrics": {
        "steps": 28,
        "tokens": 45230,
        "cost": 0.47,
        "duration": 28.3
      },
      "trajectory_url": "/demos/reddit-search-traditional.json"
    }
  ]
}
```

### Copy to Demo UI

```bash
# Copy trajectory files
cp demos/*/trajectory.json demo-ui/public/demos/

# Rename with demo ID
mv demo-ui/public/demos/trajectory.json \
   demo-ui/public/demos/reddit-search-traditional.json

# Copy video files (for traditional mode demos)
mkdir -p demo-ui/public/demos/reddit-search-traditional/videos
cp demos/reddit-search-traditional/videos/*.webm \
   demo-ui/public/demos/reddit-search-traditional/videos/

# Copy manifest
cp demos/index.json demo-ui/public/demos/index.json
```

### Adding Video to Manifest

Update `demo-ui/public/demos/index.json` to include video URL:

```json
{
  "demos": [
    {
      "id": "reddit-search-traditional",
      "title": "Reddit Search - Traditional Mode",
      "mode": "traditional",
      "video_url": "/demos/reddit-search-traditional/videos/recording.webm",
      "trajectory_url": "/demos/reddit-search-traditional.json",
      ...
    }
  ]
}
```

**Video Display in UI**:
- Videos are automatically shown for **Traditional mode** demos when `video_url` is present
- Replaces the screenshot section with an embedded video player
- Supports both WebM and MP4 formats
- Shows actual browser navigation during execution
- AWI/Permission modes still show screenshots (no video needed)

### Batch Processing Script

Create `browser_use/scripts/process_demos.sh`:

```bash
#!/bin/bash

DEMOS_DIR="./demos"
OUTPUT_DIR="./demo-ui/public/demos"

# Generate manifest
python browser_use/scripts/generate_manifest.py \
  --demos-dir "$DEMOS_DIR" \
  --output "$OUTPUT_DIR/index.json"

# Copy all trajectory files
for demo_dir in "$DEMOS_DIR"/*; do
  if [ -d "$demo_dir" ]; then
    demo_id=$(basename "$demo_dir")
    cp "$demo_dir/trajectory.json" "$OUTPUT_DIR/${demo_id}.json"
    echo "Copied ${demo_id}.json"
  fi
done

echo "✓ Processed all demos"
```

---

## Troubleshooting

### Agent Gets Stuck

**Symptoms:**
- Agent repeats same action multiple times
- No progress for 3+ steps
- Times out before completing task

**Solutions:**
```bash
# Increase max steps
--max-steps 50

# Try different model (GPT-4o is more reliable than GPT-3.5)
--model gpt-4o

# Simplify task
# Instead of: "Find posts, extract text, summarize"
# Try: "Find top 5 posts about X"
```

### API Rate Limits

**Error:** `RateLimitError: Too many requests`

**Solutions:**
```bash
# Wait 60 seconds between recordings
sleep 60 && python browser_use/scripts/record_demo.py ...

# Use different API key
export OPENAI_API_KEY=sk-different-key

# Reduce max steps
--max-steps 15
```

### Empty Trajectory

**Error:** `trajectory.json is empty or invalid`

**Causes:**
- Agent crashed before completing
- Browser session failed
- Task was impossible

**Solutions:**
```bash
# Check logs for error messages
python browser_use/scripts/record_demo.py ... 2>&1 | tee record.log

# Test task manually first
python -c "
from browser_use import Agent, Browser
import asyncio

async def test():
    agent = Agent(task='Your task', browser=Browser())
    result = await agent.run()
    print(result)

asyncio.run(test())
"
```

### Screenshots Missing

**Issue:** `screenshots/` directory is empty

**Cause:** Screenshot capture is optional and may fail silently

**Solutions:**
```bash
# Verify BrowserProfile settings in record_demo.py
profile = BrowserProfile(
    headless=False,  # Screenshots work better in headed mode
    demo_mode=True   # Enables screenshot capture
)

# Check disk space
df -h

# Verify write permissions
ls -la demos/your-demo/
```

### Token Usage Too High

**Issue:** Traditional mode uses 50K+ tokens (cost $0.50+)

**Solutions:**
```bash
# Use AWI mode instead (99.8% reduction)
--mode awi

# Reduce max steps
--max-steps 15

# Use cheaper model
--model gpt-4o-mini
```

---

## Metrics Calculation

### Token Usage

Estimated tokens per step:
- **Traditional Mode**: ~1,500-2,000 tokens/step (includes full DOM)
- **AWI Mode**: ~30-50 tokens/step (structured API only)
- **Permission Mode**: ~800-1,200 tokens/step (filtered DOM)

Formula:
```python
total_tokens = sum(step.metadata.tokens_used for step in history.history)
```

### Cost Calculation

Token costs (as of 2024):
- GPT-4o: $0.01/1K tokens
- Claude Sonnet 4.5: $0.003/1K tokens
- GPT-4o-mini: $0.0002/1K tokens

Formula:
```python
cost = (total_tokens / 1000) * price_per_1k
```

### Duration

Measured from first to last step:
```python
duration = (
    history.history[-1].metadata.step_end_time -
    history.history[0].metadata.step_start_time
)
```

---

## Demo Gallery Examples

### Example 1: Reddit Search Comparison

**Task:** "Find top 5 posts about 'browser automation' on r/programming"

**Traditional Mode:**
- Steps: 28
- Tokens: 45,230
- Cost: $0.47
- Duration: 28.3s

**AWI Mode:**
- Steps: 3 (navigate → API call → extract)
- Tokens: 89
- Cost: $0.001
- Duration: 1.2s

**Improvement:** 99.8% token reduction, 23x faster

### Example 2: E-commerce Price Comparison

**Task:** "Compare prices for wireless headphones on Amazon and BestBuy"

**Traditional Mode:**
- Steps: 32
- Tokens: 52,100
- Cost: $0.52

**Permission Mode:**
- Steps: 25 (blocked 7 tracker domains)
- Tokens: 31,200
- Cost: $0.31
- Security: Prevented data leaks to ad networks

**Improvement:** 40% token reduction + enhanced privacy

---

## Continuous Recording

### Automated Recording (Cron Job)

Record fresh demos weekly to keep content up-to-date:

```bash
# Add to crontab (runs every Sunday at 2 AM)
0 2 * * 0 cd /path/to/browser-use && bash browser_use/scripts/record_all_demos.sh

# Process and deploy
5 2 * * 0 cd /path/to/browser-use && bash browser_use/scripts/process_demos.sh && cd demo-ui && vercel --prod
```

---

## Additional Resources

- [browser-use Agent Documentation](https://docs.browser-use.com)
- [AWI Mode Guide](https://docs.browser-use.com/awi-mode)
- [AgentHistory Format Reference](../api/agent-history.md)

---

## Getting Help

If you encounter issues not covered here:

1. Check [browser-use GitHub Issues](https://github.com/browser-use/browser-use/issues)
2. Review demo recording logs: `record.log`
3. Test task manually with simpler version
4. Ask in [browser-use Discord](https://discord.gg/browser-use)
