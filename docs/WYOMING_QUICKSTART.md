# Wyoming Protocol Quick Start Guide

Get Chatterbox TTS working with Home Assistant in 5 minutes!

## Prerequisites

- Docker installed, OR
- Python 3.11+ with pip/uv

## Step 1: Start the Server

### Option A: Docker (Recommended)

```powershell
cd c:\Users\Benjamin\projects\chatterbox-tts-api\docker

# Start both OpenAI API and Wyoming Protocol servers
docker compose up -d
```

Both servers will start automatically:
- **OpenAI API**: `http://localhost:4123`
- **Wyoming Protocol**: `tcp://localhost:10200`

### Option B: Python

```powershell
cd c:\Users\Benjamin\projects\chatterbox-tts-api

# Install dependencies (if not already)
pip install -r requirements.txt

# Start both servers (Wyoming enabled by default)
python main.py
```

## Step 2: Add to Home Assistant

1. **Open Home Assistant**
   - Go to **Settings** → **Devices & Services**
   - Click **+ Add Integration**

2. **Search for "Wyoming"**
   - Select "Wyoming Protocol"

3. **Enter Connection Details**
   - **Host**: Your Chatterbox server IP (e.g., `192.168.1.100`)
   - **Port**: `10200`
   - Click **Submit**

4. **Verify Connection**
   - You should see "Chatterbox TTS" appear as a device
   - Check the list of available voices

## Step 3: Test It

### Quick Test in Home Assistant

1. Go to **Developer Tools** → **Services**
2. Select service: `tts.speak`
3. Choose entity: `tts.chatterbox_tts`
4. Enter target: `media_player.your_speaker`
5. Enter data:
   ```yaml
   message: "Hello from Chatterbox TTS!"
   ```
6. Click **Call Service**

### Use in an Automation

```yaml
automation:
  - alias: "Morning Greeting"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: tts.speak
        data:
          entity_id: media_player.bedroom_speaker
          message: "Good morning! Time to wake up."
        target:
          entity_id: tts.chatterbox_tts
```

## Configuration Options

### Disable Wyoming (Run OpenAI API Only)

If you only want the OpenAI-compatible API:

```bash
# Environment variable
ENABLE_WYOMING=false python main.py

# Or with Docker
ENABLE_WYOMING=false docker compose up
```

### Change Wyoming Port

```bash
# Environment variable
WYOMING_PORT=10201 python main.py

# Or with Docker
WYOMING_PORT=10201 docker compose up
```

## Troubleshooting

### Can't Connect?

**Check if server is running:**
```powershell
# Test if ports are open
Test-NetConnection -ComputerName localhost -Port 4123  # OpenAI API
Test-NetConnection -ComputerName localhost -Port 10200 # Wyoming
```

**Check firewall:**
```powershell
# Allow ports through Windows Firewall
New-NetFirewallRule -DisplayName "Chatterbox OpenAI API" -Direction Inbound -LocalPort 4123 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Chatterbox Wyoming TTS" -Direction Inbound -LocalPort 10200 -Protocol TCP -Action Allow
```

### No Audio?

1. **Verify speaker entity** in Home Assistant works with other TTS
2. **Check logs:**
   ```powershell
   # Docker
   docker compose logs chatterbox-tts
   
   # Python (check console output)
   ```

### Wrong Voice?

List available voices:
```powershell
# Using curl
curl http://localhost:4123/v1/audio/voices
```

Set specific voice in Home Assistant:
```yaml
service: tts.speak
data:
  entity_id: media_player.bedroom
  message: "Hello!"
  voice: my_custom_voice  # Use exact name from voice library
```

## Next Steps

- **Upload custom voices**: Use the web frontend at `http://localhost:4321`
- **Set default voice**: Visit Voice Library in the frontend
- **Advanced config**: See [full documentation](WYOMING_PROTOCOL.md)

## Common Use Cases

### Voice Notifications
```yaml
- service: tts.speak
  data:
    message: "Someone is at the front door"
    entity_id: media_player.living_room
```

### Dynamic Messages
```yaml
- service: tts.speak
  data:
    message: "The temperature is {{ states('sensor.temperature') }} degrees"
    entity_id: media_player.kitchen
```

### Multiple Speakers
```yaml
- service: tts.speak
  target:
    entity_id:
      - media_player.living_room
      - media_player.bedroom
      - media_player.kitchen
  data:
    message: "Dinner is ready!"
```

## Getting Help

- **Full Documentation**: [WYOMING_PROTOCOL.md](WYOMING_PROTOCOL.md)
- **Voice Library**: [VOICE_LIBRARY_MANAGEMENT.md](VOICE_LIBRARY_MANAGEMENT.md)
- **API Docs**: [API_README.md](API_README.md)
- **GitHub Issues**: [Report a problem](https://github.com/travisvn/chatterbox-tts-api/issues)
