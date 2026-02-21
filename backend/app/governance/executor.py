import hashlib
import json
import logging
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class ActionResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    dry_run: bool = True


class ValidationError(Exception):
    pass


class Validator:
    """Lightweight validation layer to prevent obviously destructive actions.

    This is intentionally conservative: it implements simple heuristics rather
    than trying to be a full policy engine. Real deployments should replace
    or augment this with a proper policy engine (OPA, Rego, etc.).
    """

    FORBIDDEN_SSH_PATTERNS = ["rm -rf", ":(){:|:&};:", "shutdown", "reboot"]

    @staticmethod
    def validate_k8s_manifest(manifest: str) -> bool:
        if not manifest.strip():
            raise ValidationError("Empty manifest")
        # crude check: manifest must contain apiVersion and kind
        if "apiVersion:" not in manifest or "kind:" not in manifest:
            raise ValidationError("Manifest missing apiVersion or kind")
        return True

    @staticmethod
    def validate_ssh_command(command: str) -> bool:
        low = command.lower()
        for pat in Validator.FORBIDDEN_SSH_PATTERNS:
            if pat in low:
                raise ValidationError(f"SSH command contains forbidden pattern: {pat}")
        return True

    @staticmethod
    def validate_webhook_url(url: str) -> bool:
        if not (url.startswith("https://") or url.startswith("http://")):
            raise ValidationError("Webhook URL must be http(s)")
        return True


class Executor:
    """Executor provides safe, auditable actions for remediation.

    It supports a dry-run mode by default. When `dry_run=False` it will
    attempt to execute the requested actions using the host environment's
    tools (kubectl, ssh, curl) or available Python libraries.
    """

    def __init__(self, dry_run: bool = True, audit_log_path: Optional[str] = None):
        self.dry_run = dry_run
        self.audit_log_path = audit_log_path or "/tmp/devsick_action_audit.log"

    def _audit(self, action: str, details: Dict):
        record = {"action": action, "details": details}
        payload = json.dumps(record, sort_keys=True)
        digest = hashlib.sha256(payload.encode()).hexdigest()
        entry = json.dumps({"record": record, "sha256": digest})
        with open(self.audit_log_path, "a", encoding="utf-8") as fh:
            fh.write(entry + "\n")

    def patch_k8s_manifest(self, manifest_yaml: str, namespace: str = "default") -> ActionResult:
        Validator.validate_k8s_manifest(manifest_yaml)
        self._audit("patch_k8s_manifest", {"namespace": namespace, "dry_run": self.dry_run})
        if self.dry_run:
            return ActionResult(success=True, stdout="validated (dry-run)", dry_run=True)

        kubectl = shutil.which("kubectl")
        if not kubectl:
            return ActionResult(success=False, stderr="kubectl not found on PATH", dry_run=False)

        try:
            p = subprocess.run([kubectl, "apply", "-f", "-", "-n", namespace], input=manifest_yaml.encode(), capture_output=True, check=False)
            return ActionResult(success=(p.returncode == 0), stdout=p.stdout.decode(), stderr=p.stderr.decode(), dry_run=False)
        except Exception as e:
            return ActionResult(success=False, stderr=str(e), dry_run=False)

    def scale_deployment(self, name: str, replicas: int, namespace: str = "default") -> ActionResult:
        if not name:
            raise ValidationError("Deployment name required")
        self._audit("scale_deployment", {"name": name, "replicas": replicas, "namespace": namespace, "dry_run": self.dry_run})
        if self.dry_run:
            return ActionResult(success=True, stdout=f"would scale {name} to {replicas} replicas", dry_run=True)

        kubectl = shutil.which("kubectl")
        if not kubectl:
            return ActionResult(success=False, stderr="kubectl not found", dry_run=False)

        try:
            p = subprocess.run([kubectl, "scale", "deployment", name, f"--replicas={replicas}", "-n", namespace], capture_output=True, check=False)
            return ActionResult(success=(p.returncode == 0), stdout=p.stdout.decode(), stderr=p.stderr.decode(), dry_run=False)
        except Exception as e:
            return ActionResult(success=False, stderr=str(e), dry_run=False)

    def restart_deployment(self, name: str, namespace: str = "default") -> ActionResult:
        if not name:
            raise ValidationError("Deployment name required")
        self._audit("restart_deployment", {"name": name, "namespace": namespace, "dry_run": self.dry_run})
        if self.dry_run:
            return ActionResult(success=True, stdout=f"would restart deployment {name}", dry_run=True)

        kubectl = shutil.which("kubectl")
        if not kubectl:
            return ActionResult(success=False, stderr="kubectl not found", dry_run=False)

        try:
            p = subprocess.run([kubectl, "rollout", "restart", "deployment", name, "-n", namespace], capture_output=True, check=False)
            return ActionResult(success=(p.returncode == 0), stdout=p.stdout.decode(), stderr=p.stderr.decode(), dry_run=False)
        except Exception as e:
            return ActionResult(success=False, stderr=str(e), dry_run=False)

    def run_ssh_command(self, host: str, user: str, command: str, port: int = 22, timeout: int = 10) -> ActionResult:
        Validator.validate_ssh_command(command)
        self._audit("run_ssh_command", {"host": host, "user": user, "command": command, "port": port, "dry_run": self.dry_run})
        if self.dry_run:
            return ActionResult(success=True, stdout=f"would ssh {user}@{host}:{port} '{command}'", dry_run=True)

        try:
            # Try to use system ssh if available for simplicity
            ssh = shutil.which("ssh")
            if ssh:
                target = f"{user}@{host}"
                cmd = [ssh, "-p", str(port), target, command]
                p = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
                return ActionResult(success=(p.returncode == 0), stdout=p.stdout.decode(), stderr=p.stderr.decode(), dry_run=False)

            # Fallback: if paramiko is available, use it
            try:
                import paramiko
            except Exception:
                return ActionResult(success=False, stderr="no ssh client available", dry_run=False)

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, port=port, username=user, timeout=timeout)
            stdin, stdout, stderr = client.exec_command(command)
            out = stdout.read().decode()
            err = stderr.read().decode()
            client.close()
            return ActionResult(success=True, stdout=out, stderr=err, dry_run=False)
        except Exception as e:
            return ActionResult(success=False, stderr=str(e), dry_run=False)

    def trigger_webhook(self, url: str, payload: Dict, headers: Optional[Dict] = None) -> ActionResult:
        Validator.validate_webhook_url(url)
        self._audit("trigger_webhook", {"url": url, "payload": payload, "dry_run": self.dry_run})
        if self.dry_run:
            return ActionResult(success=True, stdout=f"would POST to {url} with payload {json.dumps(payload)}", dry_run=True)

        try:
            import requests

            r = requests.post(url, json=payload, headers=headers or {})
            return ActionResult(success=(r.status_code < 300), stdout=r.text, stderr=str(r.status_code), dry_run=False)
        except Exception as e:
            return ActionResult(success=False, stderr=str(e), dry_run=False)


__all__ = ["Executor", "Validator", "ActionResult", "ValidationError"]
