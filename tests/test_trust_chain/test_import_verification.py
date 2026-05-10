import json
import logging
from pathlib import Path

import pytest

from soul_protocol.runtime.exceptions import SoulTrustError
from soul_protocol.runtime.soul import Soul
from soul_protocol.runtime.types import Interaction


async def _build_signed_soul_dir(tmp_path: Path) -> Path:
    soul = await Soul.birth("TestSoul")
    await soul.observe(Interaction(user_input="hi", agent_output="hello"))
    await soul.observe(Interaction(user_input="more", agent_output="ok"))
    soul_dir = tmp_path / "test-soul"
    await soul.save_local(soul_dir)
    return soul_dir


@pytest.mark.asyncio
async def test_import_clean_chain_passes(tmp_path: Path):
    soul_dir = await _build_signed_soul_dir(tmp_path)

    # Should not raise any exceptions
    soul = await Soul.awaken(soul_dir)
    assert soul.name == "TestSoul"
    assert soul.trust_chain.length >= 2


@pytest.mark.asyncio
async def test_import_tampered_chain_fails(tmp_path: Path):
    soul_dir = await _build_signed_soul_dir(tmp_path)

    # Tamper with the chain by modifying the signature
    chain_file = soul_dir / "trust_chain" / "chain.json"
    data = json.loads(chain_file.read_text())

    sig = data["entries"][1]["signature"]
    data["entries"][1]["signature"] = "AAAA" + sig[4:]
    chain_file.write_text(json.dumps(data, indent=2))

    with pytest.raises(SoulTrustError) as exc_info:
        await Soul.awaken(soul_dir)

    assert "Refusing to awaken soul:" in str(exc_info.value)
    assert "signature" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_import_missing_signature_fails(tmp_path: Path):
    soul_dir = await _build_signed_soul_dir(tmp_path)

    # Tamper with the chain by clearing the signature entirely
    chain_file = soul_dir / "trust_chain" / "chain.json"
    data = json.loads(chain_file.read_text())
    data["entries"][1]["signature"] = ""
    chain_file.write_text(json.dumps(data, indent=2))

    with pytest.raises(SoulTrustError) as exc_info:
        await Soul.awaken(soul_dir)

    assert "Refusing to awaken soul" in str(exc_info.value)


@pytest.mark.asyncio
async def test_import_key_rotation_mid_chain_fails(tmp_path: Path):
    soul_dir = await _build_signed_soul_dir(tmp_path)

    # Modify the public key of the last entry to simulate an unauthorized rotation
    chain_file = soul_dir / "trust_chain" / "chain.json"
    data = json.loads(chain_file.read_text())

    # Generate a fake base64 public key (32 bytes)
    import base64

    fake_pub_key = base64.b64encode(b"X" * 32).decode("ascii")
    data["entries"][1]["public_key"] = fake_pub_key

    # Need to update payload hash and signature as well so it only fails on key binding/mismatch?
    # Wait, if we just modify the key in the JSON, the signature will be invalid.
    # But Soul.verify_chain checks pubkey binding FIRST! So it should raise mismatch.
    chain_file.write_text(json.dumps(data, indent=2))

    with pytest.raises(SoulTrustError) as exc_info:
        await Soul.awaken(soul_dir)

    assert "public key mismatch" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_import_allow_unverified_warns(tmp_path: Path, caplog):
    soul_dir = await _build_signed_soul_dir(tmp_path)

    # Tamper with the chain
    chain_file = soul_dir / "trust_chain" / "chain.json"
    data = json.loads(chain_file.read_text())
    data["entries"][1]["signature"] = ""
    chain_file.write_text(json.dumps(data, indent=2))

    # Use allow_unverified=True, which should bypass the hard fail and instead log a warning
    with caplog.at_level(logging.WARNING):
        soul = await Soul.awaken(soul_dir, allow_unverified=True)

    assert soul.name == "TestSoul"
    assert any("Awakening unverified soul" in record.message for record in caplog.records)
