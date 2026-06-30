class GraphGovernanceException(Exception):
    """Base exception for all governance-related graph interruptions."""

    pass


class NodeBlockedException(GraphGovernanceException):
    """Raised when a node execution is explicitly blocked by the constitution."""

    def __init__(self, node_name: str, reason: str, audit_id: str):
        self.node_name = node_name
        self.reason = reason
        self.audit_id = audit_id
        super().__init__(f"Node '{node_name}' was BLOCKED by governance: {reason}")


class RequiresApprovalException(GraphGovernanceException):
    """Raised when a node requires manual human approval to proceed."""

    def __init__(self, node_name: str, audit_id: str, message: str):
        self.node_name = node_name
        self.audit_id = audit_id
        self.message = message
        super().__init__(f"Node '{node_name}' requires approval: {message}")
