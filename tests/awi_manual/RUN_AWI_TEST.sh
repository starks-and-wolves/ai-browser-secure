#!/bin/bash

# AWI Mode Test Runner
# This script verifies all prerequisites and runs the full AWI mode test

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🧪 AWI MODE TEST - Prerequisites Check"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if all prerequisites are met
ALL_OK=true

# Check 1: Backend
echo -n "Checking backend (localhost:5000)... "
if curl -sf http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
    echo "   Start with: cd /Users/hritish.jain/ai_security/AWI/backend && npm run dev"
    ALL_OK=false
fi

# Check 2: Redis
echo -n "Checking Redis... "
if redis-cli -a "3N2KTrkx200fctgtodEJoc1nPAQoKu21" ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
    echo "   Start with: redis-server"
    ALL_OK=false
fi

# Check 3: AWI Discovery
echo -n "Checking AWI discovery... "
if curl -sI http://localhost:5000 2>&1 | grep -q "X-AWI-Discovery"; then
    echo -e "${GREEN}✅ Available${NC}"
else
    echo -e "${RED}❌ Not available${NC}"
    echo "   Ensure backend is running with AWI support"
    ALL_OK=false
fi

# Check 4: OpenAI API Key
echo -n "Checking OpenAI API key... "
if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✅ Set${NC}"
else
    echo -e "${YELLOW}⚠️  Not set (will use default LLM)${NC}"
fi

# Check 5: Python environment
echo -n "Checking Python environment... "
if python3 -c "import browser_use" 2>/dev/null; then
    echo -e "${GREEN}✅ browser-use installed${NC}"
else
    echo -e "${RED}❌ browser-use not installed${NC}"
    echo "   Install with: pip install -e ."
    ALL_OK=false
fi

echo ""

if [ "$ALL_OK" = true ]; then
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo -e "${GREEN}✅ All prerequisites met! Starting AWI mode test...${NC}"
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "⚠️  IMPORTANT: When the permission dialog appears:"
    echo "   1. Type 'y' and press Enter to approve"
    echo "   2. Press Enter for default agent name"
    echo "   3. Press Enter for default permissions (read,write)"
    echo "   4. Type 'y' and press Enter to confirm"
    echo ""
    echo "Starting test in 3 seconds..."
    sleep 3

    # Run the test
    cd /Users/hritish.jain/ai_security/browser-use
    python3 test_full_awi_mode.py

else
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo -e "${RED}❌ Some prerequisites are not met. Please fix the issues above.${NC}"
    echo "════════════════════════════════════════════════════════════════════════════════"
    exit 1
fi
