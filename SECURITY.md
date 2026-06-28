# Security Policy

The Neural Constitution Engine is a governance and enforcement component. A vulnerability in
NCE could allow an autonomous agent to bypass its constraints or could corrupt an audit
trail. We therefore treat security reports with the highest priority and ask that you
disclose them responsibly.

## Supported versions

NCE is in pre-alpha. No versions are production-supported yet. Once the project reaches its
first stable release, this table will be maintained:

| Version | Supported          |
| ------- | ------------------ |
| `0.x`   | Pre-release; best-effort fixes on `main` only |

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues, discussions,
or pull requests.**

Instead, use one of the following private channels:

1. **GitHub Private Vulnerability Reporting** — Use the "Report a vulnerability" button under
   the repository's **Security** tab (preferred).
2. **Email** — Send details to **security@nce.dev**. If you wish to encrypt your report,
   request our PGP key first.

Please include, as far as you are able:

- A description of the vulnerability and its potential impact.
- Steps to reproduce, or a proof of concept.
- The affected component(s) and version or commit.
- Any suggested remediation.

## What to expect

- **Acknowledgement** within **3 business days**.
- **Initial assessment** and severity triage within **10 business days**.
- Coordinated disclosure: we will agree on a timeline with you and credit you in the release
  notes unless you prefer to remain anonymous.

## Scope

In scope: the NCE engine, its evaluation pipeline, the constitution store, the audit trail,
the API service, and the dashboard.

Out of scope: vulnerabilities in third-party dependencies (please report those upstream;
notify us if NCE's default configuration meaningfully amplifies the risk), and issues that
require a compromised host or privileged local access already sufficient to defeat any
software control.

## Our commitments

- We will not pursue or support legal action against researchers who act in good faith and
  in accordance with this policy.
- We will keep you informed of remediation progress.
- We will publish a security advisory for confirmed vulnerabilities after a fix is available.
