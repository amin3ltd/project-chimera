def test_redis_keyspace_isolation():
    from services.tenancy import RedisKeyspace

    a = RedisKeyspace("tenantA")
    b = RedisKeyspace("tenantB")

    assert a.task_queue() != b.task_queue()
    assert a.review_queue() != b.review_queue()
    assert a.hitl_queue() != b.hitl_queue()
    assert a.campaign_key("camp1") != b.campaign_key("camp1")
    assert a.output_key("t1") != b.output_key("t1")
    assert a.budget_key("agent1") != b.budget_key("agent1")


def test_secrets_env_provider_get_required(monkeypatch):
    from services.secrets import Secrets, SecretNotFoundError

    # Force env provider
    monkeypatch.setenv("CHIMERA_SECRETS_PROVIDER", "env")
    monkeypatch.delenv("SOME_SECRET", raising=False)
    Secrets._provider = None  # reset singleton

    try:
        Secrets.get_required("SOME_SECRET")
        assert False, "expected SecretNotFoundError"
    except SecretNotFoundError:
        pass

    monkeypatch.setenv("SOME_SECRET", "value123")
    Secrets._provider = None
    assert Secrets.get_required("SOME_SECRET") == "value123"

