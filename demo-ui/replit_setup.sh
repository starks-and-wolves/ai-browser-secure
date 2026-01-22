#!/bin/bash
# Replit Frontend Setup Script
# Run this in your frontend Repl after importing from GitHub

echo "🚀 Browser-Use Frontend Setup for Replit"
echo "========================================="
echo ""

# Check if running on Replit
if [ -z "$REPL_ID" ]; then
    echo "⚠️  Warning: This doesn't appear to be a Replit environment"
    echo "   This script is optimized for Replit deployment"
    echo ""
fi

# Step 1: Install Node.js dependencies
echo "📦 Step 1: Installing Node.js dependencies..."
npm install
if [ $? -eq 0 ]; then
    echo "✅ Node.js dependencies installed"
else
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi
echo ""

# Step 2: Check backend URL
echo "🔗 Step 2: Checking backend URL configuration..."
if [ -f ".env.production" ]; then
    BACKEND_URL=$(grep NEXT_PUBLIC_API_URL .env.production | cut -d '=' -f2)
    if [ "$BACKEND_URL" = "https://browser-use-backend.repl.co" ]; then
        echo "⚠️  Backend URL is set to placeholder!"
        echo ""
        echo "   Please update .env.production with your actual backend URL:"
        echo "   NEXT_PUBLIC_API_URL=https://browser-use-backend.YOUR_USERNAME.repl.co"
        echo ""
        echo "   Or add it to Replit Secrets (🔒 icon):"
        echo "   Key: NEXT_PUBLIC_API_URL"
        echo "   Value: https://browser-use-backend.YOUR_USERNAME.repl.co"
        echo ""
    else
        echo "✅ Backend URL configured: $BACKEND_URL"
    fi
else
    echo "⚠️  .env.production file not found!"
    echo "   Creating from example..."
    cp .env.example .env.production
    echo "   Please update .env.production with your backend URL"
fi
echo ""

# Step 3: Build the application
echo "🏗️  Step 3: Building Next.js application..."
echo "   (This may take 1-2 minutes...)"
npm run build
if [ $? -eq 0 ]; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    echo "   Check the error messages above"
    exit 1
fi
echo ""

# Final message
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Ensure backend URL is correct in .env.production or Replit Secrets"
echo "2. Click the 'Run' button at the top to start the frontend"
echo "3. Your frontend will be available at:"
echo "   https://$REPL_SLUG.$REPL_OWNER.repl.co"
echo ""
echo "4. Update your backend's FRONTEND_URL secret with this URL"
echo ""
echo "📖 Full instructions: See ../REPLIT_DEPLOYMENT.md"
echo ""
