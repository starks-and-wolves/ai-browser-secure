# Quick Start: Recording Video Demos

This guide shows you how to quickly record a traditional mode demo with video for your demo UI.

## Prerequisites

- Python environment set up (see main README)
- OpenAI or Anthropic API key
- Browser installed (Chrome/Chromium)

## Step 1: Record Demo with Video

```bash
# Set your API key
export OPENAI_API_KEY=sk-...

# Record a traditional mode demo (video recording is automatic)
python browser_use/scripts/record_demo.py \
  --task "Search for 'browser-use' on GitHub and find the repository" \
  --output ./demos/github-search-traditional \
  --mode traditional \
  --max-steps 20

# Note: Don't use --headless flag for better video quality!
```

## Step 2: Verify Files Created

```bash
ls -R ./demos/github-search-traditional/

# Should show:
# trajectory.json          # Agent execution history
# metadata.json           # Demo metrics
# videos/
#   └── recording.webm    # Video recording!
```

## Step 3: Copy to Demo UI

```bash
# Create demo directory in public folder
mkdir -p demo-ui/public/demos/github-search-traditional

# Copy trajectory
cp demos/github-search-traditional/trajectory.json \
   demo-ui/public/demos/github-search-traditional.json

# Copy video
mkdir -p demo-ui/public/demos/github-search-traditional/videos
cp demos/github-search-traditional/videos/*.webm \
   demo-ui/public/demos/github-search-traditional/videos/
```

## Step 4: Update Manifest

Edit `demo-ui/public/demos/index.json`:

```json
{
  "demos": [
    {
      "id": "github-search-traditional",
      "title": "GitHub Search - Traditional Mode",
      "description": "Search for repository using DOM parsing with video",
      "mode": "traditional",
      "task": "Search for 'browser-use' on GitHub and find the repository",
      "metrics": {
        "steps": 15,
        "tokens": 32000,
        "cost": 0.32,
        "duration": 18.5
      },
      "trajectory_url": "/demos/github-search-traditional.json",
      "video_url": "/demos/github-search-traditional/videos/recording.webm"
    }
  ]
}
```

**Key points:**
- `video_url` points to the video file in public directory
- Only needed for traditional mode (most visual)
- AWI/Permission modes can skip video

## Step 5: Test Locally

```bash
cd demo-ui
npm run dev

# Visit: http://localhost:3000/showcase
# Select your demo
# Video should play in the player!
```

## Expected Result

The TrajectoryPlayer will show:
- ✅ **Video player** showing actual browser navigation
- ✅ Step-by-step action log synchronized with video
- ✅ Metrics (tokens, cost, duration)
- ✅ Code view of trajectory JSON

## Example Video Recording Command

**Blog Post Extraction** (Great for traditional mode):
```bash
python browser_use/scripts/record_demo.py \
  --task "Go to blog.anthropic.com and extract the title and first paragraph of the latest post" \
  --output ./demos/blog-extraction-traditional \
  --mode traditional \
  --max-steps 15
```

**E-commerce Price Comparison**:
```bash
python browser_use/scripts/record_demo.py \
  --task "Search for 'wireless headphones' on Amazon and find the top 3 products with prices" \
  --output ./demos/ecommerce-traditional \
  --mode traditional \
  --max-steps 25
```

## Tips for Better Videos

1. **Don't use headless mode** - Videos look better when browser window is visible
2. **Keep tasks focused** - 10-20 steps optimal for video length
3. **Use descriptive tasks** - "Search for X and extract Y" works well
4. **Test locally first** - Run agent manually to verify task is achievable
5. **Check video file size** - 2 FPS keeps files ~5-10MB for 20-30 second recordings

## Troubleshooting

### No video file created
- Check that `video_output_dir` is set in BrowserProfile (already done in record_demo.py)
- Verify browser has permissions to record
- Try non-headless mode

### Video too large
- Reduce FPS in record_demo.py: `video_framerate=1`
- Reduce max_steps (shorter demo = smaller video)
- Compress video after recording: `ffmpeg -i input.webm -b:v 500k output.webm`

### Video not playing in browser
- Check file path in manifest matches actual location
- Ensure video file is in `public/` directory
- Try converting to MP4: `ffmpeg -i input.webm output.mp4`

## Next Steps

- Record AWI mode demo (comparison with video demo)
- Deploy to Vercel (videos work on production too!)
- Add more demos to showcase different capabilities

---

**Time to record a demo:** ~2-3 minutes
**Total setup time:** ~10 minutes including copy to UI

Ready to record your first video demo? Follow Step 1 above!
