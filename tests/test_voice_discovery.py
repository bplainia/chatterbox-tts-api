"""
Test voice discovery functionality
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest
from app.core.voice_library import VoiceLibrary


def test_discover_empty_directory():
    """Test discovery in an empty directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        lib = VoiceLibrary(tmpdir)
        result = lib.discover_and_import_voices()
        
        assert result["imported"] == []
        assert result["skipped"] == []


def test_discover_existing_wav_file(tmp_path):
    """Test discovery of a WAV file in the directory"""
    # Create a fake WAV file
    voice_file = tmp_path / "test_voice.wav"
    voice_file.write_bytes(b"RIFF" + b"\x00" * 100)  # Minimal WAV-like data
    
    lib = VoiceLibrary(str(tmp_path))
    result = lib.discover_and_import_voices()
    
    assert "test_voice" in result["imported"]
    assert len(result["imported"]) == 1
    assert result["skipped"] == []
    
    # Verify voice is in metadata
    voices = lib.list_voices()
    assert len(voices) == 1
    assert voices[0]["name"] == "test_voice"
    assert voices[0]["discovered"] is True


def test_discover_multiple_formats(tmp_path):
    """Test discovery of multiple audio formats"""
    # Create files with different extensions
    formats = [".wav", ".mp3", ".flac", ".m4a", ".ogg"]
    for i, ext in enumerate(formats):
        voice_file = tmp_path / f"voice{i}{ext}"
        voice_file.write_bytes(b"AUDIO" + b"\x00" * 100)
    
    lib = VoiceLibrary(str(tmp_path))
    result = lib.discover_and_import_voices()
    
    assert len(result["imported"]) == 5
    assert all(f"voice{i}" in result["imported"] for i in range(5))


def test_discover_skips_non_audio_files(tmp_path):
    """Test that non-audio files are skipped"""
    # Create various non-audio files
    (tmp_path / "readme.txt").write_text("test")
    (tmp_path / "data.json").write_text("{}")
    (tmp_path / "image.png").write_bytes(b"PNG")
    
    # Create one audio file
    (tmp_path / "voice.wav").write_bytes(b"RIFF" + b"\x00" * 100)
    
    lib = VoiceLibrary(str(tmp_path))
    result = lib.discover_and_import_voices()
    
    assert result["imported"] == ["voice"]
    assert len(result["skipped"]) == 0  # Non-audio files aren't even considered


def test_discover_skips_existing_voices(tmp_path):
    """Test that already-tracked voices are not re-imported"""
    # Create and import a voice
    voice_file = tmp_path / "existing.wav"
    voice_file.write_bytes(b"RIFF" + b"\x00" * 100)
    
    lib = VoiceLibrary(str(tmp_path))
    
    # First discovery
    result1 = lib.discover_and_import_voices()
    assert "existing" in result1["imported"]
    
    # Second discovery should skip the existing voice
    result2 = lib.discover_and_import_voices()
    assert result2["imported"] == []
    assert result2["skipped"] == []


def test_discover_with_custom_language(tmp_path):
    """Test discovery with custom language setting"""
    voice_file = tmp_path / "french_voice.wav"
    voice_file.write_bytes(b"RIFF" + b"\x00" * 100)
    
    lib = VoiceLibrary(str(tmp_path))
    result = lib.discover_and_import_voices(default_language="fr")
    
    assert "french_voice" in result["imported"]
    
    # Verify language is set
    voice_info = lib.get_voice_info("french_voice")
    assert voice_info["language"] == "fr"


def test_discover_metadata_persistence(tmp_path):
    """Test that discovered voices are persisted in metadata"""
    voice_file = tmp_path / "persistent.wav"
    voice_file.write_bytes(b"RIFF" + b"\x00" * 100)
    
    # Create library and discover
    lib1 = VoiceLibrary(str(tmp_path))
    lib1.discover_and_import_voices()
    
    # Create new library instance (simulates restart)
    lib2 = VoiceLibrary(str(tmp_path))
    voices = lib2.list_voices()
    
    assert len(voices) == 1
    assert voices[0]["name"] == "persistent"


def test_discover_after_manual_upload(tmp_path):
    """Test that discovery works alongside API uploads"""
    lib = VoiceLibrary(str(tmp_path))
    
    # Upload via API
    lib.add_voice("uploaded_voice", b"AUDIO_DATA", "uploaded.wav", "en")
    
    # Add file manually to directory
    (tmp_path / "discovered_voice.wav").write_bytes(b"RIFF" + b"\x00" * 100)
    
    # Discover
    result = lib.discover_and_import_voices()
    
    assert "discovered_voice" in result["imported"]
    assert "uploaded_voice" not in result["imported"]  # Already exists
    
    # Both should be listed
    voices = lib.list_voices()
    assert len(voices) == 2
    voice_names = [v["name"] for v in voices]
    assert "uploaded_voice" in voice_names
    assert "discovered_voice" in voice_names


def test_discover_handles_special_characters_in_filename(tmp_path):
    """Test handling of filenames with special characters"""
    # Create file with spaces and special chars
    voice_file = tmp_path / "my_voice-v2.wav"
    voice_file.write_bytes(b"RIFF" + b"\x00" * 100)
    
    lib = VoiceLibrary(str(tmp_path))
    result = lib.discover_and_import_voices()
    
    assert "my_voice-v2" in result["imported"]


def test_list_voices_includes_discovered_voices(tmp_path):
    """Test that list_voices returns discovered voices"""
    # Add some files
    (tmp_path / "voice1.wav").write_bytes(b"AUDIO" + b"\x00" * 100)
    (tmp_path / "voice2.mp3").write_bytes(b"AUDIO" + b"\x00" * 100)
    
    lib = VoiceLibrary(str(tmp_path))
    lib.discover_and_import_voices()
    
    voices = lib.list_voices()
    assert len(voices) == 2
    
    # Check that discovered flag is set
    for voice in voices:
        assert voice["discovered"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
