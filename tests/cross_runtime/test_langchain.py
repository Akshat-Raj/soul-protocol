import pytest

from soul_protocol import Soul

pytest.importorskip(
    "langchain_core", reason="LangChain is not installed, skipping integration test."
)
from langchain_core.messages import SystemMessage


@pytest.mark.cross_runtime
@pytest.mark.asyncio
async def test_langchain_integration(tmp_soul_file, tmp_path):
    """A populated soul file must be exported and then imported and must contain the correct persona."""

    source_file = tmp_soul_file
    soul = await Soul.awaken(source_file)

    await soul.edit_core_memory(persona="LangChain Agent")
    await soul.note("User's favorite framework is LangChain")
    langchain_message = SystemMessage(content=soul.to_system_prompt())

    assert "LangChain Agent" in langchain_message.content
    destination_file = str(tmp_path / "langchain_exported.soul")

    await soul.export(destination_file)
    recovered_soul = await Soul.awaken(destination_file)
    assert "LangChain Agent" in recovered_soul.to_system_prompt()
    
    memories = await recovered_soul.recall("favorite framework")
    assert any("favorite framework is LangChain" in m.content for m in memories), "Semantic memory failed to persist"
