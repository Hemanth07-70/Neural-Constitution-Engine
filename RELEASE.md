# Release Process

This document outlines the standard release process for the Neural Constitution Engine.

1. **Verify CI/CD:** Ensure all GitHub Actions are green on the `main` branch.
2. **Update Version:** Bump the version in `pyproject.toml` and `__init__.py`.
3. **Generate Release Notes:** Compile a list of changes since the last release.
4. **Draft Release:** Create a new GitHub Release draft targeting `main`.
5. **Publish:** Publish the GitHub Release, which will automatically trigger the PyPI deployment workflow.
6. **Verify Package:** Test `pip install neural-constitution-engine` in a fresh environment.
