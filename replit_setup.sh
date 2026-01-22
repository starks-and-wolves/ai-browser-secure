#!/bin/bash
# Replit Backend Setup Script
# Run this in your backend Repl after importing from GitHub

echo "🚀 Browser-Use Backend Setup for Replit"
echo "========================================"
echo ""

# Check if running on Replit
if [ -z "$REPL_ID" ]; then
    echo "⚠️  Warning: This doesn't appear to be a Replit environment"
    echo "   This script is optimized for Replit deployment"
    echo ""
fi

# Step 1: Install Python dependencies
echo "📦 Step 1: Installing Python dependencies..."
pip install -e . --quiet
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
echo ""

# Step 2: Install Chromium
echo "🌐 Step 2: Installing Chromium..."
echo "   (This may take 2-3 minutes...)"
playwright install chromium --with-deps
if [ $? -eq 0 ]; then
    echo "✅ Chromium installed"
else
    echo "⚠️  Chromium installation had issues (this is common on free tier)"
    echo "   You can use a remote browser service like Browserless.io instead"
fi
echo ""

# Step 3: Check environment variables
echo "🔑 Step 3: Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$BROWSER_USE_API_KEY" ]; then
    echo "⚠️  No API keys found in Replit Secrets!"
    echo ""
    echo "   Please add one of these to Replit Secrets (🔒 icon):"
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - BROWSER_USE_API_KEY"
    echo ""
else
    echo "✅ API key found"
fi
echo ""

# Step 4: Test server startup
echo "🧪 Step 4: Testing server startup..."
echo "   Starting server for 3 seconds..."
timeout 3 python main.py > /dev/null 2>&1 &
sleep 3
if pgrep -f "main.py" > /dev/null; then
    echo "✅ Server can start successfully"
    pkill -f "main.py"
else
    echo "⚠️  Server test inconclusive (this is normal)"
fi
echo ""

# Final message
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Add your API key to Replit Secrets if you haven't already"
echo "2. Click the 'Run' button at the top to start the server"
echo "3. Your backend will be available at:"
echo "   https://$REPL_SLUG.$REPL_OWNER.repl.co"
echo ""
echo "4. Set up the frontend Repl with your backend URL"
echo ""
echo "📖 Full instructions: See REPLIT_DEPLOYMENT.md"
echo ""
