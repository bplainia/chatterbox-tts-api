"""
Wyoming Protocol server implementation for Chatterbox TTS
Enables integration with Home Assistant and other Wyoming-compatible voice assistants
"""

import asyncio
import io
import wave
from typing import Optional
from dataclasses import dataclass

from wyoming.info import Info, TtsProgram, TtsVoice, Attribution
from wyoming.server import AsyncServer
from wyoming.tts import Synthesize, SynthesizeVoice
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event

from app.core.tts_model import get_tts_model, get_model_type
from app.core.voice_library import get_voice_library
from app.config import Config


@dataclass
class WyomingConfig:
    """Configuration for Wyoming server"""
    host: str = "0.0.0.0"
    port: int = 10200
    default_voice: str = "default"
    sample_rate: int = 24000
    sample_width: int = 2
    channels: int = 1


class ChatterboxWyomingHandler:
    """Handler for Wyoming protocol events"""
    
    def __init__(self, config: WyomingConfig):
        self.config = config
        self.voice_library = get_voice_library()
        
    async def handle_event(self, event: Event) -> Optional[Event]:
        """Handle incoming Wyoming events"""
        
        if Synthesize.is_type(event.type):
            # TTS synthesis request
            synthesize = Synthesize.from_event(event)
            return await self._handle_synthesize(synthesize)
        
        return None
    
    async def _handle_synthesize(self, synthesize: Synthesize):
        """Handle TTS synthesis request"""
        text = synthesize.text
        voice_name = None
        
        # Get voice name if specified
        if synthesize.voice and synthesize.voice.name:
            voice_name = synthesize.voice.name
        
        # Resolve voice path
        voice_path = self._resolve_voice_path(voice_name)
        
        # Generate speech
        audio_data = await self._generate_speech(text, voice_path)
        
        # Send audio chunks
        return self._create_audio_response(audio_data)
    
    def _resolve_voice_path(self, voice_name: Optional[str]) -> str:
        """Resolve voice name to file path"""
        if not voice_name or voice_name == "default":
            # Use default voice
            default_voice = self.voice_library.get_default_voice()
            if default_voice:
                voice_path = self.voice_library.get_voice_path(default_voice)
                if voice_path:
                    return voice_path
            return Config.VOICE_SAMPLE_PATH
        
        # Try to get voice from library
        voice_path = self.voice_library.get_voice_path(voice_name)
        if voice_path:
            return voice_path
        
        # Fallback to default
        return Config.VOICE_SAMPLE_PATH
    
    async def _generate_speech(self, text: str, voice_path: str) -> bytes:
        """Generate speech audio from text"""
        model = get_tts_model()
        
        # Generate audio
        audio = await asyncio.to_thread(
            model.generate,
            text=text,
            voice_sample_path=voice_path,
            exaggeration=Config.EXAGGERATION,
            cfg_weight=Config.CFG_WEIGHT,
            temperature=Config.TEMPERATURE
        )
        
        # Convert to WAV format
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.config.channels)
            wav_file.setsampwidth(self.config.sample_width)
            wav_file.setframerate(self.config.sample_rate)
            wav_file.writeframes(audio.tobytes())
        
        return buffer.getvalue()
    
    def _create_audio_response(self, audio_data: bytes):
        """Create Wyoming audio response from audio data"""
        # Parse WAV to get audio samples
        with wave.open(io.BytesIO(audio_data), 'rb') as wav_file:
            rate = wav_file.getframerate()
            width = wav_file.getsampwidth()
            channels = wav_file.getnchannels()
            frames = wav_file.readframes(wav_file.getnframes())
        
        # Create audio events
        events = [
            AudioStart(
                rate=rate,
                width=width,
                channels=channels
            ).event(),
            AudioChunk(
                audio=frames,
                rate=rate,
                width=width,
                channels=channels
            ).event(),
            AudioStop().event()
        ]
        
        return events


class ChatterboxWyomingServer(AsyncServer):
    """Wyoming protocol server for Chatterbox TTS"""
    
    def __init__(self, config: WyomingConfig):
        self.config = config
        self.handler = ChatterboxWyomingHandler(config)
        
        # Create server info
        info = self._create_info()
        
        super().__init__(
            info,
            host=config.host,
            port=config.port
        )
    
    def _create_info(self) -> Info:
        """Create Wyoming server info with available voices"""
        voice_library = get_voice_library()
        voices = voice_library.list_voices()
        
        # Create voice list
        wyoming_voices = []
        
        # Add default voice
        wyoming_voices.append(
            TtsVoice(
                name="default",
                description="Default Chatterbox voice",
                installed=True
            )
        )
        
        # Add voices from library
        for voice in voices:
            wyoming_voices.append(
                TtsVoice(
                    name=voice["name"],
                    description=f"Custom voice: {voice['name']}",
                    installed=True
                )
            )
        
        # Create TTS program info
        tts = TtsProgram(
            name="chatterbox-tts",
            description="Chatterbox TTS - High quality voice cloning",
            attribution=Attribution(
                name="Resemble AI",
                url="https://github.com/resemble-ai/chatterbox"
            ),
            installed=True,
            voices=wyoming_voices
        )
        
        return Info(
            tts=[tts]
        )
    
    async def handle_event(self, event: Event) -> Optional[Event]:
        """Handle Wyoming protocol events"""
        return await self.handler.handle_event(event)


async def start_wyoming_server(
    host: str = "0.0.0.0",
    port: int = 10200,
    default_voice: str = "default"
):
    """Start the Wyoming protocol server"""
    config = WyomingConfig(
        host=host,
        port=port,
        default_voice=default_voice
    )
    
    server = ChatterboxWyomingServer(config)
    
    print(f"🎙️ Starting Wyoming Protocol server on {host}:{port}")
    print(f"   Default voice: {default_voice}")
    print(f"   Model: {get_model_type()}")
    
    await server.run()


def run_wyoming_server(
    host: str = "0.0.0.0",
    port: int = 10200,
    default_voice: str = "default"
):
    """Run the Wyoming server (blocking)"""
    asyncio.run(start_wyoming_server(host, port, default_voice))


if __name__ == "__main__":
    # Run standalone Wyoming server
    run_wyoming_server()
