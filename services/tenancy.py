"""
Multi-tenancy primitives.

This module provides:
- A TenantContext model
- A RedisKeyspace helper to ensure tenant-isolated keys/queues

Goal: prevent cross-tenant data leakage when multiple tenants share the same
Redis instance (and later, the same persistence layers).
"""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_TENANT_ID = "default"


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str = DEFAULT_TENANT_ID

    def normalized(self) -> "TenantContext":
        tid = (self.tenant_id or DEFAULT_TENANT_ID).strip()
        return TenantContext(tenant_id=tid or DEFAULT_TENANT_ID)


@dataclass(frozen=True)
class RedisKeyspace:
    """
    Generates tenant-scoped Redis keys.

    Convention:
      tenant:<tenant_id>:<namespace>[:<id>...]
    """

    tenant_id: str = DEFAULT_TENANT_ID

    def _t(self) -> str:
        tid = (self.tenant_id or DEFAULT_TENANT_ID).strip() or DEFAULT_TENANT_ID
        return f"tenant:{tid}"

    # Queues (shared names but tenant-prefixed)
    def task_queue(self) -> str:
        return f"{self._t()}:queue:task"

    def review_queue(self) -> str:
        return f"{self._t()}:queue:review"

    def hitl_queue(self) -> str:
        return f"{self._t()}:queue:hitl"

    # Campaign state
    def campaign_key(self, campaign_id: str) -> str:
        return f"{self._t()}:campaign:{campaign_id}"

    def campaign_state_field(self) -> str:
        return "state"

    def campaign_version_field(self) -> str:
        return "version"

    # Output storage
    def output_key(self, task_id: str) -> str:
        return f"{self._t()}:output:{task_id}"

    # Budget tracking
    def budget_key(self, agent_id: str) -> str:
        return f"{self._t()}:budget:{agent_id}"

