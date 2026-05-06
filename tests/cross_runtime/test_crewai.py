import pytest

from soul_protocol import Soul

try:
    from crewai import Agent
except ImportError as e:
    pytest.skip(f"Importing CrewAI failed({e})", allow_module_level=True)


@pytest.mark.cross_runtime
@pytest.mark.asyncio
async def test_crewai_integration(tmp_soul_file, tmp_path):
    """A populated soul file must be exported and then imported and must contain the correct persona."""

    source_file = tmp_soul_file
    soul = await Soul.awaken(source_file)

    await soul.edit_core_memory(persona="CrewAI Agent")

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
