# Browser-Use Demo UI

A Next.js showcase application demonstrating browser-use's three execution modes: Traditional (DOM parsing), Permission (security-focused), and AWI Mode (structured API).

**Live Demo:** _(Add your Vercel URL here after deployment)_

## Features

- **Interactive Trajectory Player**: Step-by-step playback of agent executions with screenshots
- **Metrics Visualization**: Token usage, cost, and performance comparisons
- **Three-Mode Comparison**: Side-by-side showcase of Traditional vs Permission vs AWI
- **Responsive Design**: Mobile-friendly with touch controls
- **Accessibility**: WCAG 2.1 compliant with keyboard navigation and screen reader support
- **Smooth Animations**: Framer Motion powered transitions and loading states

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
demo-ui/
├── app/                          # Next.js App Router
│   ├── page.tsx                 # Landing page
│   ├── showcase/page.tsx        # Demo viewer
│   ├── layout.tsx               # Root layout
│   └── globals.css              # Global styles
├── components/
│   ├── showcase/                # Demo components
│   │   ├── TrajectoryPlayer.tsx    # Step-by-step player
│   │   ├── MetricsVisualization.tsx # Charts and metrics
│   │   ├── ScreenshotCarousel.tsx  # Image carousel
│   │   └── CodeBlock.tsx           # Syntax-highlighted JSON
│   └── shared/                  # Shared components
│       ├── LoadingSkeletons.tsx # Loading states
│       └── CodeBlock.tsx        # Reusable code viewer
├── lib/
│   ├── types.ts                 # TypeScript types (mirrors Python models)
│   └── demoLoader.ts            # Demo loading utilities
├── public/demos/                # Pre-recorded demos
│   ├── index.json              # Demo manifest
│   ├── reddit-search-traditional.json
│   └── reddit-search-awi.json
└── package.json
```

## Key Metrics Displayed

### Traditional Mode (DOM Parsing)
- **Token Usage**: 45,230 tokens
- **Cost**: $0.47 per task
- **Duration**: 28.3 seconds
- **Steps**: 28 agent actions

### AWI Mode (Structured API)
- **Token Usage**: 89 tokens (99.8% reduction)
- **Cost**: $0.001 per task (500x cheaper)
- **Duration**: 1.2 seconds (23x faster)
- **Steps**: 3 API calls

## Technology Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion 11
- **Deployment**: Vercel
- **Build Tool**: Next.js built-in (Turbopack)

## Adding New Demos

### 1. Record Demo

```bash
cd ../  # Go to repository root
source .venv/bin/activate

python browser_use/scripts/record_demo.py \
  --task "Your task description" \
  --output ./demos/your-demo-id \
  --mode traditional
```

### 2. Process Demo

```bash
# Copy trajectory to public directory
cp demos/your-demo-id/trajectory.json \
   demo-ui/public/demos/your-demo-id.json

# Update manifest
python browser_use/scripts/generate_manifest.py \
  --demos-dir ./demos \
  --output ./demo-ui/public/demos/index.json
```

### 3. Verify

```bash
cd demo-ui
npm run dev

# Visit http://localhost:3000/showcase
# New demo should appear in selector
```

See [docs/demo-ui/recording-demos.md](../docs/demo-ui/recording-demos.md) for detailed guide.

## Deployment

### Deploy to Vercel

```bash
# Option 1: Via dashboard
# 1. Push to GitHub
# 2. Import project on vercel.com
# 3. Set root directory to "demo-ui"
# 4. Deploy

# Option 2: Via CLI
vercel --prod
```

See [docs/demo-ui/deployment.md](../docs/demo-ui/deployment.md) for full deployment guide.

## Accessibility Features

### WCAG 2.1 Compliance

- ✅ Semantic HTML (`<main>`, `<nav>`, `<button>`)
- ✅ ARIA labels for all interactive elements
- ✅ Keyboard navigation (Tab, Enter, Escape)
- ✅ Focus indicators (blue outline on all focusable elements)
- ✅ Skip links for screen readers
- ✅ Touch-friendly controls (minimum 44px tap targets)
- ✅ Color contrast ratios meet AA standards

### Keyboard Shortcuts

- **Tab**: Navigate between interactive elements
- **Enter**: Activate buttons and links
- **Escape**: Close modals (if Phase 3 implemented)
- **Arrow Keys**: Navigate timeline steps

## Performance Optimization

### Bundle Size

```
Route (app)              Size       First Load JS
┌ ○ /                   1.7 kB     143 kB
└ ○ /showcase          6.22 kB     147 kB
```

### Implemented Optimizations

- **Static Generation**: All pages pre-rendered at build time
- **Code Splitting**: Automatic with Next.js dynamic imports
- **CSS Purging**: Tailwind removes unused styles
- **Compression**: Vercel automatically compresses assets

## Roadmap

### Phase 1-2 (Completed)
- ✅ Next.js setup with TypeScript + Tailwind
- ✅ Pre-recorded demo showcase
- ✅ Interactive trajectory player
- ✅ Metrics visualization
- ✅ Responsive design

### Phase 3 (Optional - Not Started)
- [ ] Live execution with WebSocket streaming
- [ ] User API key input
- [ ] Security controls (domain whitelist)
- [ ] Real-time token usage tracking

### Phase 4 (In Progress)
- ✅ Animations (Framer Motion)
- ✅ Loading skeletons
- ✅ Accessibility improvements
- ✅ Deployment documentation
- [ ] Vercel deployment

## License

This demo UI is part of the [browser-use](https://github.com/browser-use/browser-use) project.

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Vercel Deployment Guide](https://vercel.com/docs)
- [browser-use Documentation](https://docs.browser-use.com)

## Support

- **Issues**: [GitHub Issues](https://github.com/browser-use/browser-use/issues)
- **Discussions**: [GitHub Discussions](https://github.com/browser-use/browser-use/discussions)

---

**Built with ❤️ using browser-use**
