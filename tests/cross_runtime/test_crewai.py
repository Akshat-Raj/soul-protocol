import pytest

from soul_protocol import Soul

pytest.importorskip(
    "crewai", reason="CrewAI is not installed, skipping integration test."
)
from crewai import Agent


@pytest.mark.cross_runtime
@pytest.mark.asyncio
async def test_crewai_integration(tmp_soul_file, tmp_path):
    """A populated soul file must be exported and then imported and must contain the correct persona."""

    source_file = tmp_soul_file
    soul = await Soul.awaken(source_file)

    await soul.edit_core_memory(persona="CrewAI Agent")
    await soul.note("User's favorite framework is CrewAI")

    crew_agent = Agent(
        role="Programmer",
        goal="Write code",
        backstory=soul.to_system_prompt(),
        verbose=False,
        allow_delegation=False,
    )

    assert "CrewAI Agent" in crew_agent.backstory

    destination_file = str(tmp_path / "crewai_exported.soul")
    await soul.export(destination_file)

    recovered_soul = await Soul.awaken(destination_file)
    assert "CrewAI Agent" in recovered_soul.to_system_prompt()
    
    memories = await recovered_soul.recall("favorite framework")
    assert any("favorite framework is CrewAI" in m.content for m in memories), "Semantic memory failed to persist"

