# Frontend — Dashboard (reserved)

> **Status: not yet implemented.** This directory is reserved for the NCE dashboard. No
> Next.js application, dependencies, or business logic exist yet. Implementation begins in
> **M3** (see [`../docs/roadmap.md`](../docs/roadmap.md)).

The frontend will be the human interface to NCE: authoring and versioning constitutions,
simulating proposals against a draft constitution before publishing, and exploring the audit
trail. Its design is specified in
[`../docs/architecture.md`](../docs/architecture.md#recommended-frontend-structure-nextjs--not-yet-implemented).

## Planned layout

```
frontend/
├── app/                       # Next.js App Router (routes, layouts)
│   ├── constitutions/         # Authoring and version management
│   ├── audit/                 # Audit trail explorer
│   └── layout.tsx
├── components/                # Reusable presentational components
├── features/                  # Feature modules (state + UI per domain area)
├── lib/                       # API client, formatting, utilities
├── hooks/                     # Reusable React hooks
├── types/                     # Shared TypeScript types (mirroring the API contract)
├── public/                    # Static assets
├── package.json
└── Dockerfile
```

When implementation starts, this README will be replaced with setup, run, and build
instructions.
