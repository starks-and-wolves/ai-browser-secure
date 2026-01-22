#!/bin/bash

# Record all demos for the demo UI
# Make sure OPENAI_API_KEY or ANTHROPIC_API_KEY is set before running

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEMOS_DIR="$PROJECT_ROOT/demo-ui/public/demos"

echo "🎬 Recording Browser-Use Demos"
echo "Output directory: $DEMOS_DIR"
echo ""

# Create demos directory
mkdir -p "$DEMOS_DIR"

# Demo 1: Reddit Search - Traditional Mode
echo "📹 Recording Demo 1: Reddit Search (Traditional Mode)"
python "$SCRIPT_DIR/record_demo.py" \
	--task "Go to reddit.com/r/programming and find the top 5 posts about 'browser automation'. Extract the post titles and upvote counts." \
	--output "$DEMOS_DIR/reddit-search-traditional" \
	--mode traditional \
	--max-steps 30
echo "✅ Demo 1 complete"
echo ""

# Demo 2: Reddit Search - AWI Mode
echo "📹 Recording Demo 2: Reddit Search (AWI Mode)"
echo "⚠️  Note: This requires the AWI backend to be running at https://ai-browser-security.onrender.com"
python "$SCRIPT_DIR/record_demo.py" \
	--task "Go to https://ai-browser-security.onrender.com and list the top 3 blog posts, then add a comment 'Great post!' to the first one." \
	--output "$DEMOS_DIR/reddit-search-awi" \
	--mode awi \
	--max-steps 10
echo "✅ Demo 2 complete"
echo ""

# Demo 3: E-commerce - Permission Mode
echo "📹 Recording Demo 3: E-commerce (Permission Mode)"
echo "⚠️  This will prompt for approvals - approve google.com and github.com, deny others"
python "$SCRIPT_DIR/record_demo.py" \
	--task "Search Google for 'wireless headphones price' and visit the first two shopping sites to compare prices." \
	--output "$DEMOS_DIR/ecommerce-permission" \
	--mode permission \
	--max-steps 15
echo "✅ Demo 3 complete"
echo ""

# Demo 4: Form Filling - Sensitive Data
echo "📹 Recording Demo 4: Form Filling (Sensitive Data)"
python "$SCRIPT_DIR/record_demo.py" \
	--task "Go to github.com/browser-use/browser-use and find the number of stars, then navigate to the issues page and count open issues." \
	--output "$DEMOS_DIR/form-filling-sensitive" \
	--mode traditional \
	--max-steps 10
echo "✅ Demo 4 complete"
echo ""

# Generate index.json manifest
echo "📝 Generating demo manifest (index.json)"
python "$SCRIPT_DIR/generate_manifest.py" --demos-dir "$DEMOS_DIR"
echo "✅ Manifest generated"
echo ""

echo "🎉 All demos recorded successfully!"
echo "Demos saved to: $DEMOS_DIR"
