import pytest

from soul_protocol import Interaction, Soul

pytest.importorskip(
    "pocketpaw", reason="Pocketpaw is not installed, skipping integration test."
)
from pocketpaw.config import Settings
from pocketpaw.soul.manager import SoulManager

@pytest.mark.cross_runtime
@pytest.mark.asyncio
async def test_pocketpaw_integration(tmp_soul_file, tmp_path):
    """A populated soul file must be exported and then imported by pocketpaw and must contain the correct persona."""

    source_file = tmp_soul_file
    soul = await Soul.awaken(source_file)

    await soul.edit_core_memory(persona="PocketPaw Agent")
    await soul.note("User is using soul-protocol")

    exported_file = str(tmp_path / "pocketpaw_exported.soul")
    await soul.export(exported_file)

    settings = Settings(soul_path=str(tmp_path / "pocketpaw_loaded.soul"), soul_name="pocketpaw_loaded")
    manager = SoulManager(settings)
    await manager.import_from_file(exported_file)

    assert manager.soul is not None, "PocketPaw failed to load the soul"
    assert manager.soul.get_core_memory().persona == "PocketPaw Agent", "Core memory failed to persist through PocketPaw import"
    
    memories = await manager.soul.recall("soul-protocol")
    assert any("soul-protocol" in m.content for m in memories), "Sequential memory failed to persist"