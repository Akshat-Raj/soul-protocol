import shutil
import subprocess

import pytest

from soul_protocol import Soul, Interaction


@pytest.mark.cross_runtime
@pytest.mark.asyncio
async def test_pocketpaw_integration(tmp_soul_file, tmp_path):
    """A populated soul file must be exported and then imported and must contain the correct persona."""

    source_file = tmp_soul_file
    soul = await Soul.awaken(source_file)
    
    await soul.edit_core_memory(persona="I am a PocketPaw Agent.")
    
    await soul.observe(Interaction(
        user_input="Hello PocketPaw!",
        agent_output="Hello User!",
        channel="test_channel"
    ))
    
    start_file = str(tmp_path / "pocketpaw_start.soul")
    await soul.export(start_file)
    
    exported_file = str(tmp_path / "pocketpaw_exported.soul")
    
    if not shutil.which("pocketpaw"):
        pytest.skip("PocketPaw cli tool 'pocketpaw' not found in PATH.")
        
    try:
        subprocess.run(["pocketpaw", "import", "--file", start_file, "--id", "test_agent"], check=True)
        
        subprocess.run(["pocketpaw", "export", "--id", "test_agent", "--out", exported_file], check=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"PocketPaw CLI execution failed: {e}")

    recovered_soul = await Soul.awaken(exported_file)
    
    assert "PocketPaw Agent" in recovered_soul.to_system_prompt()
    
    assert recovered_soul.state.interaction_count >= 1