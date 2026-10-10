"""A persisted title outranks a construction-time hint after external renames."""

from types import SimpleNamespace
from unittest.mock import patch

from agent.conversation_loop import _bot_chat_prompt_stale
from agent.system_prompt import _bot_mode_parts
from tools.bot_mode_dm import _session_title


class _TitleDB:
    def __init__(self, title):
        self.title = title

    def get_session(self, sid):
        return {"id": sid, "title": self.title}

    def get_session_title(self, sid):
        return self.title


def test_external_rename_overrides_stale_hint_across_bot_gates(tmp_path):
    db = _TitleDB("Bot Chat")
    agent = SimpleNamespace(
        _session_db=db, session_id="sid", _session_title_hint="Old title",
        _bot_mode_protocol=True,
    )
    with patch("tools.bot_mode_probe.get_bot_mode_protocol_section", return_value="bot rules"), patch(
        "agent.system_prompt._agent_home", return_value=tmp_path
    ), patch("tools.bot_mode_probe.epoch_line", return_value="epoch"):
        assert _bot_mode_parts(agent) == ["bot rules", "epoch"]
    with patch("tools.bot_mode_probe.stored_prompt_capability_stale", return_value=False), patch(
        "tools.bot_mode_probe.stored_bot_chat_prompt_needs_upgrade", return_value=True
    ):
        assert _bot_chat_prompt_stale(agent, "old prompt") is True
    assert _session_title(agent) == "Bot Chat"

    db.title = ""
    agent._session_title_hint = "Bot Chat"
    with patch("tools.bot_mode_probe.get_bot_mode_protocol_section", return_value="bot rules"):
        assert _bot_mode_parts(agent) == []
    with patch("tools.bot_mode_probe.stored_prompt_capability_stale", return_value=False), patch(
        "tools.bot_mode_probe.stored_bot_chat_prompt_needs_upgrade", return_value=True
    ):
        assert _bot_chat_prompt_stale(agent, "old prompt") is False
    assert _session_title(agent) == ""


def test_persisted_clear_does_not_restore_hint(tmp_path):
    from hermes_state import SessionDB

    with SessionDB(db_path=tmp_path / "state.db") as db:
        db.create_session("sid", source="cli")
        db.set_session_title("sid", "Bot Chat")
        agent = SimpleNamespace(
            _session_db=db, session_id="sid", _session_title_hint="Bot Chat",
        )
        assert _session_title(agent) == "Bot Chat"
        db.set_session_title("sid", "Other title")
        assert _session_title(agent) == "Other title"
        db.set_session_title("sid", "")
        assert _session_title(agent) == ""
        assert agent._session_title_hint == "Bot Chat"  # no mid-turn mutation


def test_unpersisted_construction_title_remains_available():
    agent = SimpleNamespace(
        _session_db=_TitleDB(None), session_id="sid", _session_title_hint="Bot Chat",
    )
    agent._session_db.get_session = lambda _sid: None
    assert _session_title(agent) == "Bot Chat"
