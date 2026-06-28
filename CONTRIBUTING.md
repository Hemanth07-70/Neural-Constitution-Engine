# Contributing to the Neural Constitution Engine

Thank you for your interest in contributing to NCE. This project governs how autonomous
agents are allowed to act — correctness, clarity, and traceability matter more here than
raw velocity. We ask that all contributions reflect that bar.

> **Project status:** NCE is in its foundational phase (M0). The application code does not
> exist yet. The most valuable contributions right now are to the **design and
> documentation**: sharpening the vision, pressure-testing the architecture, and shaping
> the roadmap. See [`docs/roadmap.md`](docs/roadmap.md).

## Ways to contribute

- **Design feedback** — Open an issue challenging or extending the
  [architecture](docs/architecture.md) or [vision](docs/vision.md).
- **Documentation** — Improve clarity, fix errors, add examples.
- **Proposals (RFCs)** — Propose new capabilities or significant changes (see below).
- **Code** — Once implementation milestones open, pick up scoped issues.

## Design-first culture

NCE follows a **design-first** workflow. Anything that changes a public interface, the
evaluation semantics, the data model, or the security posture should begin as a written
proposal before code is written.

1. Open an issue describing the problem and your proposed approach.
2. For substantial changes, submit an RFC (a Markdown document under `docs/rfcs/`, added
   when that process opens) describing motivation, design, alternatives, and risks.
3. Reach rough consensus with maintainers before implementation.

This keeps the engine's behavior predictable and its history legible — properties a
governance tool cannot compromise on.

## Development workflow

> The commands below describe the *intended* workflow. They will become live as the
> `backend/` and `frontend/` directories are implemented (see the roadmap).

1. **Fork and branch.** Create a topic branch from `main`:
   - `feat/<short-description>` for features
   - `fix/<short-description>` for bug fixes
   - `docs/<short-description>` for documentation
2. **Commit with [Conventional Commits](https://www.conventionalcommits.org/).**
   Example: `feat(engine): add modify-verdict support`.
   Allowed types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`.
3. **Keep changes focused.** One logical change per pull request.
4. **Write tests** for any behavioral change once the test suite exists.
5. **Open a pull request** against `main` with a clear description and links to the
   relevant issue or RFC.

## Pull request expectations

- The PR title follows Conventional Commits.
- The description explains *what* changed and *why*, not just *how*.
- Documentation and `CHANGELOG.md` (the `[Unreleased]` section) are updated when relevant.
- CI passes (once CI is established).
- At least one maintainer approval is required to merge.

## Code of conduct

All participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By
participating, you agree to uphold it.

## Reporting security issues

Do **not** open public issues for security vulnerabilities. Follow the process in
[`SECURITY.md`](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE).
