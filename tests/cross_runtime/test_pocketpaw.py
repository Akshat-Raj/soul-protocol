import pytest
from soul_protocol import Soul, Interaction

@pytest.mark.cross_runtime
@pytest.mark.asyncio
async def test_pocketpaw_integration(tmp_soul_file, tmp_path):
    """A populated soul file must be exported and then imported and must contain the correct persona."""

    source_file = str(tmp_soul_file)
    soul = await Soul.awaken(source_file)

    # semantic memory
    await soul.edit_core_memory(persona="PocketPaw Agent")
    await soul.remember("Some semantic memory")

    number_of_interactions = len(soul.state.recent_interactions)

    # episodic memory
    await soul.observe(Interaction(
        user_input="Hello PocketPaw!",
        agent_output="Hello User!",
        channel="test_channel"
    ))

    exported_file = str(tmp_path / "pocketpaw_exported.soul")
    await soul.export(exported_file)

    recovered_soul = await Soul.awaken(exported_file)

    assert "PocketPaw Agent" in recovered_soul.to_system_prompt(), "Core memory failed to persist."

    semantic_facts = [entry.content for entry in recovered_soul._memory._semantic.facts()]
    assert any("semantic" in fact for fact in semantic_facts), "Semantic memory failed to persist."

    assert len(recovered_soul.state.recent_interactions) == number_of_interactions+1, "Episodic history failed to persist."