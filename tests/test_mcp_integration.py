import asyncio


def test_mcp_news_server_resource_and_tool():
    """
    Ensures the MCP client can connect via stdio to a real MCP server process
    and perform read_resource + call_tool end-to-end.
    """

    async def _run():
        from services.mcp_client import create_news_mcp_client

        client = create_news_mcp_client()
        await client.connect()

        txt = await client.read_resource("news://latest")
        assert isinstance(txt, str)
        assert txt.strip()
        assert "- " in txt

        out = await client.call_tool("fetch_trends", {"topic": "AI agents", "limit": 2})
        assert isinstance(out, dict)
        assert "trends" in out
        assert isinstance(out["trends"], list)
        assert len(out["trends"]) >= 1

        await client.aclose()

    asyncio.run(_run())


def test_perception_poller_emits_tasks_for_relevant_headlines():
    async def _run():
        from services.perception import PerceptionPoller, SemanticFilter

        emitted = []

        def sink(task):
            emitted.append(task)

        poller = PerceptionPoller(
            semantic_filter=SemanticFilter(relevance_threshold=0.2),
            task_sink=sink,
            campaign_id="test",
        )
        await poller.start()

        tasks = await poller.poll_once(goals=["AI agents", "AI disclosure"])
        assert tasks, "expected at least one task from relevant headlines"
        assert emitted == tasks
        assert all(t.task_type == "analyze_trends" for t in tasks)

        await poller.aclose()

    asyncio.run(_run())

