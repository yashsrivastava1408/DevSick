import os
from typing import Optional

from .executor import Executor, ValidationError


class SafeExecutor:
    """Wraps `Executor` to enforce justification and require an approval token
    to perform non-dry-run actions.

    Usage:
      - By default all actions are dry-run.
      - Provide `approval_token` matching the `GOVERNANCE_APPROVAL_TOKEN` env
        variable to execute actions for real (temporary promotion).
    """

    def __init__(self, approval_env_var: str = "GOVERNANCE_APPROVAL_TOKEN"):
        self.approval_env_var = approval_env_var
        self.executor = Executor(dry_run=True)

    def perform_with_safety(self, func_name: str, *args, justification: Optional[str] = None, approval_token: Optional[str] = None, **kwargs):
        if not justification or len(justification.strip()) < 10:
            raise ValidationError("Justification required (min 10 characters)")

        approved = False
        env_token = os.environ.get(self.approval_env_var)
        if approval_token and env_token and approval_token == env_token:
            approved = True

        # Audit via underlying executor
        self.executor._audit("safety_check", {"func": func_name, "justification": justification, "approved": approved})

        func = getattr(self.executor, func_name)
        if not approved:
            return func(*args, **kwargs)

        # Temporarily promote executor to live mode
        prev = self.executor.dry_run
        try:
            self.executor.dry_run = False
            return func(*args, **kwargs)
        finally:
            self.executor.dry_run = prev


__all__ = ["SafeExecutor"]
