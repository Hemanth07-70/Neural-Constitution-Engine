from typing import Annotated, Any

from typing_extensions import TypedDict


def add_audits(left: list[str] | None, right: list[str] | None) -> list[str]:
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right


def add_rewrites(left: list[dict[str, Any]] | None, right: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right


class GovernanceState(TypedDict):
    """
    Standard typed dict mixin for LangGraph states.
    By inheriting from this, users can automatically track governance outputs.
    """

    # A list of audit IDs generated during the graph run
    audit_ids: Annotated[list[str], add_audits]

    # Store the most recent verdict for the current node (if rewritten or allowed)
    last_verdict: str

    # If a node was rewritten, this contains the original vs rewritten payload
    rewrite_history: Annotated[list[dict[str, Any]], add_rewrites]
