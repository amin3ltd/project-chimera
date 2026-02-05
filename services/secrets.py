"""
Secrets management.

SRS requires secrets-manager style injection (keys are never hard-coded and are
not logged). This module provides a pluggable secret provider with:
- Environment variable provider (default; works in local/dev and CI)
- Optional AWS Secrets Manager provider (if boto3 is installed and configured)

The goal is to provide a single interface for reading secrets in runtime code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


class SecretNotFoundError(RuntimeError):
    pass


class SecretProvider:
    def get(self, name: str) -> str | None:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass(frozen=True)
class EnvSecretProvider(SecretProvider):
    prefix: str = ""

    def get(self, name: str) -> str | None:
        key = f"{self.prefix}{name}" if self.prefix else name
        return os.environ.get(key)


@dataclass(frozen=True)
class AwsSecretsManagerProvider(SecretProvider):
    """
    Optional provider. Requires:
      - boto3 installed
      - AWS credentials available via the environment/instance role
    """

    region_name: str | None = None
    secret_id_prefix: str = ""

    def get(self, name: str) -> str | None:
        try:
            import boto3  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("boto3 is required for AWS Secrets Manager provider") from e

        sid = f"{self.secret_id_prefix}{name}" if self.secret_id_prefix else name
        client = boto3.client("secretsmanager", region_name=self.region_name)
        resp = client.get_secret_value(SecretId=sid)
        # Prefer SecretString; binary secrets not supported in this repo.
        return resp.get("SecretString")


def _provider_from_env() -> SecretProvider:
    provider = (os.environ.get("CHIMERA_SECRETS_PROVIDER") or "env").strip().lower()
    if provider == "env":
        return EnvSecretProvider(prefix=os.environ.get("CHIMERA_SECRETS_ENV_PREFIX", ""))
    if provider in ("aws", "aws_secrets_manager", "secretsmanager"):
        return AwsSecretsManagerProvider(
            region_name=os.environ.get("AWS_REGION"),
            secret_id_prefix=os.environ.get("CHIMERA_AWS_SECRET_PREFIX", ""),
        )
    raise ValueError(f"Unknown secrets provider: {provider}")


class Secrets:
    """
    Facade used by runtime code.
    """

    _provider: SecretProvider | None = None

    @classmethod
    def provider(cls) -> SecretProvider:
        if cls._provider is None:
            cls._provider = _provider_from_env()
        return cls._provider

    @classmethod
    def get(cls, name: str) -> str | None:
        return cls.provider().get(name)

    @classmethod
    def get_required(cls, name: str) -> str:
        value = cls.get(name)
        if value is None or value == "":
            raise SecretNotFoundError(
                f"Missing required secret: {name}. "
                f"Set it in the environment or configure CHIMERA_SECRETS_PROVIDER."
            )
        return value

