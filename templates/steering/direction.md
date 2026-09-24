# Direction: what this project is, and is not

> **Edit this file to match YOUR project.** This is the product-direction steering document. `CLAUDE.md`
> loads on every task and stays short. This file loads only when **scope is decided**: the planning,
> architecture, and epic-slicing skills read it if it exists (`.claude/references/direction.md`, or
> `direction.md` at the repo root), and a triage workflow can check every new issue or PR against it.
> Every clause has a name so a decline can cite it: `direction.md §single-datastore`.
> Shipped defaults describe the AI Tutor, the course's demo codebase. Replace them with yours.

> **Until you have rewritten it, this file is wrong for your repo.** If you are an agent reading
> this and it still describes the AI Tutor rather than the codebase around you, say so in your
> report and judge the change against `CLAUDE.md` and the other references instead. Steering the
> wrong way is worse than not steering.

This file is committed and shared by the whole team. Edit it deliberately, in a reviewed PR, so triage stays
consistent across people and across runs.

## What this IS

- **§tutor-over-published-content** A tutor that answers from the creator's published material (YouTube
  transcripts and community content), with sources and timestamps on every answer. The value is grounded
  answers, not chat.
- **§single-datastore** One Postgres database with pgvector. Ingestion, users, and retrieval share it. A
  second datastore is a direction call, not a ticket.
- **§membership-gates-depth** Anyone can ask; linked members get the extended corpus. Membership is
  verified against the community platform, never self-declared.
- **§source-adapters** New content sources land as adapters behind the existing ingestion interface, so a
  source is a slice, not a rewrite.

## What this is NOT

- **§not-a-general-chatbot** Not a general assistant. Questions outside the corpus get an honest "not
  covered," not a confident answer from model memory.
- **§not-multi-tenant** One deployment serves one creator's corpus. No per-tenant isolation, billing, or
  workspace switching inside the app. Serving another creator means another deployment.
- **§not-a-content-editor** The app reads published content; it never edits, hosts, or republishes it.
- **§no-second-datastore** No Redis, no separate vector service, no document store alongside Postgres.
  Cache and search live in the one database until a measured limit says otherwise.

## Aspirational architecture

Where the engineering is going. Do not reject a change for failing to complete this; reject new coupling
that makes it materially harder.

- **§slices-own-their-surface** Each feature is a vertical slice that owns its routes, service, repository,
  and tests. Cross-cutting concerns live in shared modules that slices import; slices do not import each
  other.
- **§retrieval-behind-one-interface** Every retrieval strategy sits behind the same interface, so ranking
  changes are a swap, not a rewrite of callers.

## Open questions (no stance yet)

Direction calls not yet made. Work that touches these should surface the question for an explicit decision
rather than be silently accepted or rejected.

- **§open-multi-language** Whether the corpus and answers support languages other than English.
- **§open-voice-input** Whether voice input belongs in the product or stays a client concern.

## How to evolve this doc

- Add an IS or IS NOT line when a triage forces a direction call.
- Move an open question to IS or IS NOT once decided.
- Cite the clause when declining or re-scoping: `direction.md §not-a-general-chatbot`.
- Keep entries to one or two lines. This is for fast lookup during planning and triage, not a manifesto.
