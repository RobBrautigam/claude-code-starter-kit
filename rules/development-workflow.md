# Development Workflow

## Localhost-first development
- Always run the project locally during development using `npm run dev`, `python -m uvicorn`, or whatever the project's dev server command is.
- Never deploy to production just to see changes. Localhost gives instant feedback.
- When starting a work session, start the local dev server if it is not already running.
- Only commit and push when a feature or fix is verified working locally.
- The deploy (auto-deploy from GitHub via Railway / Vercel / etc.) happens as a consequence of pushing to main, not as a development step.

### Safety: backend processes that hit production
- Frontend-only dev servers (`npm run dev` for Next.js, Vite, etc.) are safe to auto-start. They serve static files locally and don't touch production databases.
- Python backend (uvicorn / FastAPI) may be auto-started when a session needs live data to verify UI or run integration tests. Prefer `python -m uvicorn src.api.main:app --reload --port 8000` since this boots FastAPI + routes only, not the scheduler / bot.
- **Do NOT auto-start aggressive pollers** (e.g., Telegram bot pollers, scheduled jobs). They can spike production database load. Start them only when the user explicitly asks.
- Orphaned processes survive VS Code restarts and run indefinitely at the OS level. Verify cleanup at session end (`tasklist | findstr python` on Windows, `ps aux | grep python` on macOS/Linux) and stop any processes you started, by process id only. Background `run_in_background: true` tasks must be stopped before session close, and a stopped task is checked in the process table afterwards. The full discipline lives in `process-hygiene.md`.
- When in doubt about whether a process touches production, ask before starting it.

## Component library standard
- All new frontend projects use shadcn/ui as the default component library.
- Before building any UI component from scratch, check if a shadcn/ui component exists for that purpose.
- When starting a new frontend project, run `npx shadcn@latest init` during setup.
- UI components from shadcn live in `src/components/ui/`. Custom components live in `src/components/`.
- Use Lucide React for icons. Never use emojis as UI icons.

## Design system
- Every project with a frontend should have a `DESIGN.md` in the project root describing colors, typography, spacing, components, and visual rules.
- Reference the design system for all UI decisions: colors, spacing, typography, component patterns.
- If no design system exists yet, ask the user about visual direction before building UI.
- Maintain visual consistency within each project. Don't mix styles across pages.

## Code quality tools
- All new frontend projects should have ESLint configured.
- Use TypeScript for all new frontend projects.
- Use path aliases (`@/components`, `@/lib`, `@/utils`) for clean imports.

## Testing
- Write tests for critical paths: API endpoints, data sync functions, auth flows.
- Run tests before shipping. Don't claim something works without evidence.
- Use the test suite as a regression safety net, especially when making changes to shared utilities.

## Error monitoring
- All production apps should have structured error logging.
- When an error occurs in production, there should be a way to see what happened without SSH-ing into the server (Sentry, LogTail, Better Stack, etc.).
