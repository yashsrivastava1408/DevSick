#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Ensure backend package is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.governance.executor import Executor
from app.governance.sandbox import SafeExecutor


def fmt(res):
    return f"success={res.success}, dry_run={res.dry_run}, stdout={res.stdout!r}, stderr={res.stderr!r}"


def main():
    print("Demo: SafeExecutor (dry-run by default)")
    se = SafeExecutor()

    print("1) Dry-run scale_deployment:")
    r = se.perform_with_safety("scale_deployment", "web", 3, justification="testing dry-run behavior")
    print(fmt(r))

    print("\n2) Attempt with wrong approval token (still dry-run):")
    r = se.perform_with_safety("scale_deployment", "web", 2, justification="urgent fix needed", approval_token="wrong-token")
    print(fmt(r))

    print("\n3) Set correct token and attempt promotion (may fail if kubectl absent):")
    os.environ["GOVERNANCE_APPROVAL_TOKEN"] = "secret-token-123"
    r = se.perform_with_safety("scale_deployment", "web", 1, justification="scale down for maintenance", approval_token="secret-token-123")
    print(fmt(r))


if __name__ == "__main__":
    main()
