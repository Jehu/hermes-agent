"""Compatibility contract for Agent Zero's pinned fasta2a==0.5.0 client."""

from pydantic import TypeAdapter
from fasta2a.schema import Message, Part, Task

from plugins.platforms.a2a import protocol


def test_text_part_validates_with_fasta2a_050():
    parsed = TypeAdapter(Part).validate_python(protocol.text_part("hello"))
    assert parsed == {"kind": "text", "text": "hello"}


def test_agent_message_validates_with_fasta2a_050():
    parsed = TypeAdapter(Message).validate_python(
        protocol.text_message(protocol.ROLE_AGENT, "hello", "ctx-1")
    )
    assert parsed["kind"] == "message"
    assert parsed["role"] == "agent"
    assert parsed["parts"][0] == {"kind": "text", "text": "hello"}


def test_completed_task_validates_with_fasta2a_050():
    parsed = TypeAdapter(Task).validate_python(
        protocol.build_task("task-1", "ctx-1", protocol.STATE_COMPLETED, "done")
    )
    assert parsed["kind"] == "task"
    assert parsed["status"]["state"] == "completed"
    assert parsed["status"]["message"]["role"] == "agent"
    assert parsed["artifacts"][0]["parts"][0]["kind"] == "text"
