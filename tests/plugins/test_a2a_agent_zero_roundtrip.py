"""Live Agent Zero client contract against the Hermes A2A adapter."""

from __future__ import annotations

import asyncio
import importlib.util

import pytest
from _pytest.monkeypatch import MonkeyPatch

from tests.plugins.test_a2a_phase23 import _make_live_adapter


def test_agent_zero_fasta2a_client_roundtrip():
    # Standard runner does not include the external Agent Zero checkout.
    if importlib.util.find_spec("helpers") is None:
        pytest.skip("external Agent Zero helpers unavailable; add its checkout to PYTHONPATH")
    pytest.importorskip("fasta2a.client")
    from helpers.fasta2a_client import AgentConnection

    async def run() -> None:
        monkeypatch = MonkeyPatch()
        monkeypatch.delenv("A2A_BEARER_TOKEN", raising=False)
        monkeypatch.delenv("A2A_PEER_TOKENS", raising=False)
        adapter, base_url = _make_live_adapter(monkeypatch)
        try:
            assert await adapter.connect() is True
            connection = AgentConnection(base_url, timeout=15)
            try:
                card = await connection.get_agent_card()
                assert card["name"]
                response = await connection.send_message("hello from Agent Zero")
                result = response["result"]
                assert result["kind"] == "task"
                assert result["status"]["state"] == "completed"
                assert result["status"]["message"]["role"] == "agent"
            finally:
                await connection.close()
        finally:
            await adapter.disconnect()
            monkeypatch.undo()

    asyncio.run(run())
