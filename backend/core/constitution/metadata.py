"""Immutable models for constitution metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Resolution:
    """How conflicts are resolved for this document."""

    strategy: str
    default_verdict: str


@dataclass(slots=True, frozen=True)
class Metadata:
    """Top-level metadata for a Constitution document."""

    id: str
    version: str
    scope: str
    title: str | None = None
    description: str | None = None
    author: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    status: str | None = None
    extends: str | None = None
