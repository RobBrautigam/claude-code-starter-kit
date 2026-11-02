# Model the Best-of-Best in Every Decision

When making any engineering, architectural, UX, or UI decision - frontend or backend - reference and model leading SaaS products in the market. The aesthetic and operational ethos: premium, modern, cutting-edge, clean, simple, effective, efficient, useful, functional.

This applies to every decision type. It's a global standard, not a per-project preference.

## Reference set

Use these as the baseline for "what does good look like":

| Domain | Companies to study |
|---|---|
| Product UX, navigation, onboarding | Linear, Notion, Stripe, Vercel, Figma, Anthropic |
| Auth, account, team management | Linear, Stripe, Vercel, Notion, GitHub |
| API design, SDKs, developer ergonomics | Stripe, Twilio, Anthropic, Supabase |
| Dashboards, data visualization | Vercel, Linear, Datadog, PostHog |
| Forms, settings, configuration screens | Stripe, Linear, Notion |
| Marketing-site polish, conversion design | Stripe, Linear, Vercel, Apple |
| Pricing pages, plan ladders | Stripe, Linear, Notion, Vercel |
| Empty states, error states, loading states | Linear, Notion, Stripe |
| Component libraries, design tokens | Vercel (Geist), Linear, Apple HIG, Material 3, shadcn |
| Documentation | Stripe, Anthropic, Supabase, Vercel |

## How to apply

- Lead every recommendation with how a best-in-class product solves the same problem ("Linear does X because Y; we should apply that here because Z").
- Do not recommend generic, dated, or cargo-culted patterns.
- When trade-offs exist, frame them in terms of which leading product made which trade-off and why.
- For UI: look up the actual current implementation when in doubt - these companies set the bar and it moves.
- For backend: the same applies (Stripe's idempotency keys, Anthropic's tool-use schema, Supabase's RLS posture, Linear's optimistic UI on top of GraphQL).
- Resist "good enough" - premium products require premium engineering.
- When something objectively better than what the leaders do exists, propose that instead and explain the leap.

## When NOT to apply

- Internal-only tools where polish doesn't pay back (one-off scripts in `tmp/`, throwaway local utilities) - be pragmatic.
- When user-facing scope is genuinely a 5-minute fix and adding "cutting-edge" patterns just slows shipping.
- When a leader's pattern is itself dated or being moved away from.
