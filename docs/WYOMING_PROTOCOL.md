# Wyoming Protocol Integration

This guide explains how to use Chatterbox TTS with Wyoming Protocol, enabling integration with Home Assistant and other Wyoming-compatible voice assistants.

## What is Wyoming Protocol?

Wyoming Protocol is a communication protocol developed for voice assistants, particularly Home Assistant. It allows voice assistant components (wake word detection, speech-to-text, text-to-speech) to communicate with each other over a TCP connection.

## Features

- ✅ **Full Wyoming Protocol Support** - Compatible with Home Assistant and other Wyoming clients
- ✅ **Voice Library Integration** - Access all your custom cloned voices
- ✅ **Default Voice Support** - Uses your configured default voice
- ✅ **Easy Setup** - Docker container or standalone Python script
- ✅ **Low Latency** - Direct TCP communication for faster response times

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start both API and Wyoming server (enabled by default)
cd docker
docker compose up

# Or start all services including frontend
docker compose --profile frontend up
```

Both servers will start automatically:
- **OpenAI API**: `http://localhost:4123`
- **Wyoming Protocol**: `tcp://localhost:10200`

### Option 2: Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run both servers (Wyoming enabled by default)
python main.py

# Or run OpenAI API only
ENABLE_WYOMING=false python main.py
```

### Configuration Options

**Change Wyoming Port:**
```bash
WYOMING_PORT=10201 python main.py
```

**Change Default Voice:**
```bash
DEFAULT_VOICE=my_custom_voice python main.py
```

**Disable Wyoming:**
```bash
ENABLE_WYOMING=false python main.py
```

## Home Assistant Integration

### 1. Add Wyoming Integration

In Home Assistant, add the Wyoming integration:

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Wyoming Protocol"
4. Enter the connection details:
   - **Host**: IP address of your Chatterbox server (e.g., `192.168.1.100`)
   - **Port**: `10200` (default Wyoming port)

### 2. Configure Voice Selection

Once integrated, you can select voices in Home Assistant:

```yaml
# configuration.yaml
tts:
  - platform: wyoming
    service: chatterbox-tts
    voice: my_custom_voice  # Use any voice from your voice library
```

### 3. Use in Automations

```yaml
# Example automation
automation:
  - alias: "Welcome Home"
    trigger:
      - platform: state
        entity_id: person.john
        to: "home"
    action:
      - service: tts.speak
        data:
          entity_id: media_player.living_room
          message: "Welcome home!"
        target:
          entity_id: tts.chatterbox_tts
```

## Available Voices

The Wyoming server automatically exposes all voices from your voice library:

- **`default`** - The default voice (system or library default)
- **Custom voices** - All voices uploaded to your voice library

To see available voices:

```bash
# Using wyoming CLI (install: pip install wyoming)
wyoming-cli info tcp://localhost:10200
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WYOMING_HOST` | `0.0.0.0` | Host to bind the server to |
| `WYOMING_PORT` | `10200` | Port to bind the server to |
| `WYOMING_DEFAULT_VOICE` | `default` | Default voice to use |

### Docker Compose

```yaml
# Wyoming is enabled by default in the main service
services:
  chatterbox-tts:
    ports:
      - "4123:4123"  # OpenAI API
      - "10200:10200"  # Wyoming Protocol
    environment:
      ENABLE_WYOMING: true
      WYOMING_PORT: 10200
      DEFAULT_VOICE: my_custom_voice
```

### Python

```bash
# Run both servers
python main.py

# Or with custom settings
WYOMING_PORT=10200 DEFAULT_VOICE=my_custom_voice python main.py
```

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Home Assistant │◄───────►│ Wyoming Protocol │
│   (Wyoming      │   TCP   │     Server       │
│   Integration)  │  10200  │   (Chatterbox)   │
└─────────────────┘         └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  Chatterbox TTS  │
                            │      Model       │
                            └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  Voice Library   │
                            │  (Custom Voices) │
                            └──────────────────┘
```

## Testing

### Test with wyoming CLI

```bash
# Install wyoming client
pip install wyoming

# Get server info
wyoming-cli info tcp://localhost:10200

# Synthesize text
echo "Hello from Chatterbox TTS!" | wyoming-cli synthesize \
  --uri tcp://localhost:10200 \
  --voice default \
  --output test.wav
```

### Test with Python

```python
import asyncio
from wyoming.client import AsyncClient
from wyoming.tts import Synthesize

async def test_tts():
    client = AsyncClient("localhost", 10200)
    await client.connect()
    
    # Send synthesis request
    await client.write_event(
        Synthesize(
            text="Hello from Chatterbox TTS!",
            voice="default"
        ).event()
    )
    
    # Receive audio
    async for event in client.read_events():
        if event.type == "audio-chunk":
            print(f"Received {len(event.data)} bytes of audio")
    
    await client.disconnect()

asyncio.run(test_tts())
```

## Troubleshooting

### Server Won't Start

```bash
# Check if ports are already in use
netstat -ano | findstr :4123  # OpenAI API
netstat -ano | findstr :10200 # Wyoming

# Try different ports
WYOMING_PORT=10201 python main.py
```

### Home Assistant Can't Connect

1. **Check firewall**: Ensure ports 4123 and 10200 are open
2. **Verify IP address**: Use the correct IP of your Chatterbox server
3. **Check logs**: Look at server output for errors
4. **Verify Wyoming is enabled**: Check that `ENABLE_WYOMING=true` (default)

### Voice Not Found

```bash
# List available voices
curl http://localhost:4123/v1/audio/voices

# Set default voice for Wyoming server
DEFAULT_VOICE="voice_name_here" python main.py
```

### Audio Quality Issues

The Wyoming server uses the same quality settings as the main API:

- Adjust `EXAGGERATION`, `CFG_WEIGHT`, `TEMPERATURE` environment variables
- Or modify the `Config` values in your `.env` file

## Performance

### Latency Comparison

| Method | Average Latency | Use Case |
|--------|----------------|----------|
| Wyoming Protocol | 500-800ms | Voice assistants, real-time |
| REST API | 800-1200ms | Applications, batch processing |
| REST API (streaming) | 300-500ms (first chunk) | Web apps, progressive playback |

### Resource Usage

- **CPU**: Similar to REST API (~2-5% idle, 50-80% during synthesis)
- **Memory**: ~500MB-2GB depending on model
- **Network**: TCP connection per client (minimal overhead)

## Advanced Usage

### Multiple Wyoming Servers

Run multiple servers with different default voices:

```bash
# English voice on port 10200
WYOMING_PORT=10200 DEFAULT_VOICE=english_voice python main.py &

# Spanish voice on port 10201
WYOMING_PORT=10201 DEFAULT_VOICE=spanish_voice python main.py &

# French voice on port 10202
WYOMING_PORT=10202 DEFAULT_VOICE=french_voice python main.py &
```

Or with Docker:

```yaml
services:
  chatterbox-english:
    ports:
      - "10200:10200"
    environment:
      WYOMING_PORT: 10200
      DEFAULT_VOICE: english_voice
  
  chatterbox-spanish:
    ports:
      - "10201:10200"  # Map host port to container port
    environment:
      WYOMING_PORT: 10200  # Container internal port
      DEFAULT_VOICE: spanish_voice
```

### Custom Protocol Handler

You can extend the Wyoming handler for custom behavior:

```python
from app.core.wyoming_server import ChatterboxWyomingHandler

class CustomHandler(ChatterboxWyomingHandler):
    async def _generate_speech(self, text: str, voice_path: str) -> bytes:
        # Add custom preprocessing
        text = self.preprocess_text(text)
        
        # Call parent implementation
        return await super()._generate_speech(text, voice_path)
    
    def preprocess_text(self, text: str) -> str:
        # Your custom logic here
        return text.upper()
```

### Integration with Voice Assistant Pipelines

```yaml
# Home Assistant configuration
assist_pipeline:
  - name: "Chatterbox Voice Assistant"
    conversation_engine: homeassistant
    conversation_language: en
    tts_engine: wyoming
    tts_language: en
    tts_voice: my_custom_voice
    wake_word_engine: openwakeword
    wake_word_id: "ok_nabu"
```

## References

- [Wyoming Protocol Specification](https://github.com/rhasspy/wyoming)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
- [Chatterbox TTS API Documentation](../README.md)
- [Voice Library Management](VOICE_LIBRARY_MANAGEMENT.md)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs: `docker compose logs wyoming`
3. Open an issue on GitHub with logs and configuration details
