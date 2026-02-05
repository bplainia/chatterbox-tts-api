# Docker Images Quick Reference

## Available Images

All images are available on Docker Hub at: `<your-dockerhub-username>/chatterbox-tts-api`

### Image Variants

| Pull Command | Use Case | Requirements |
|-------------|----------|--------------|
| `docker pull <username>/chatterbox-tts-api:latest` | Standard deployment, auto-detects GPU | CPU or NVIDIA GPU |
| `docker pull <username>/chatterbox-tts-api:latest-frontend` | API + Web UI | CPU or NVIDIA GPU |
| `docker pull <username>/chatterbox-tts-api:latest-cpu` | CPU-only deployment | CPU only |
| `docker pull <username>/chatterbox-tts-api:latest-gpu` | NVIDIA GPU optimized | NVIDIA GPU + CUDA |
| `docker pull <username>/chatterbox-tts-api:latest-uv` | Fast builds, auto-detect | CPU or NVIDIA GPU |
| `docker pull <username>/chatterbox-tts-api:latest-uv-gpu` | Fastest GPU builds | NVIDIA GPU + CUDA |
| `docker pull <username>/chatterbox-tts-api:latest-blackwell` | Next-gen NVIDIA Blackwell | Blackwell GPU |

## Quick Start Examples

### Standard API

```bash
docker run -d \
  --name chatterbox-tts \
  -p 4123:4123 \
  -e HF_TOKEN=your_huggingface_token \
  <username>/chatterbox-tts-api:latest
```

Access API at: `http://localhost:4123`

### With Frontend

```bash
docker run -d \
  --name chatterbox-tts-frontend \
  -p 4123:4123 \
  -p 4321:4321 \
  -e HF_TOKEN=your_huggingface_token \
  <username>/chatterbox-tts-api:latest-frontend
```

Access:
- API: `http://localhost:4123`
- Frontend: `http://localhost:4321`

### GPU Accelerated

```bash
docker run -d \
  --name chatterbox-tts-gpu \
  --gpus all \
  -p 4123:4123 \
  -e HF_TOKEN=your_huggingface_token \
  <username>/chatterbox-tts-api:latest-gpu
```

### CPU Only (Multi-arch)

```bash
docker run -d \
  --name chatterbox-tts-cpu \
  -p 4123:4123 \
  -e HF_TOKEN=your_huggingface_token \
  -e DEVICE=cpu \
  <username>/chatterbox-tts-api:latest-cpu
```

Works on x86_64 and ARM64 (Apple Silicon, Raspberry Pi).

## Docker Compose Examples

### Simple GPU Setup

```yaml
version: '3.8'
services:
  chatterbox-tts:
    image: <username>/chatterbox-tts-api:latest-gpu
    container_name: chatterbox-tts
    ports:
      - '4123:4123'
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - TTS_MODEL_TYPE=multilingual
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped
```

### With Frontend

```yaml
version: '3.8'
services:
  chatterbox-tts:
    image: <username>/chatterbox-tts-api:latest-frontend
    container_name: chatterbox-tts-frontend
    ports:
      - '4123:4123'
      - '4321:4321'
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - TTS_MODEL_TYPE=multilingual
    volumes:
      - tts-cache:/cache
      - tts-voices:/voices
    restart: unless-stopped

volumes:
  tts-cache:
  tts-voices:
```

### CPU Only with Persistent Storage

```yaml
version: '3.8'
services:
  chatterbox-tts:
    image: <username>/chatterbox-tts-api:latest-cpu
    container_name: chatterbox-tts-cpu
    ports:
      - '4123:4123'
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - TTS_MODEL_TYPE=multilingual
      - DEVICE=cpu
    volumes:
      - ./cache:/cache
      - ./voices:/voices
      - ./data:/data
    restart: unless-stopped
```

## Version Tags

Replace `:latest` with specific versions:

- `:latest` - Latest stable from main branch
- `:v1.0.0` - Specific version (semver)
- `:v1.0` - Latest patch in v1.0.x
- `:v1` - Latest minor in v1.x.x
- `:main` - Latest development build
- `:develop` - Latest development branch

Examples:
```bash
# Specific version
docker pull <username>/chatterbox-tts-api:v1.2.3-gpu

# Latest v1.x with frontend
docker pull <username>/chatterbox-tts-api:v1-frontend

# Development build
docker pull <username>/chatterbox-tts-api:develop-cpu
```

## Image Sizes (Approximate)

| Variant | Compressed | Uncompressed |
|---------|-----------|--------------|
| CPU | ~3.5 GB | ~10 GB |
| GPU | ~5.5 GB | ~15 GB |
| UV | ~3.0 GB | ~9 GB |
| UV-GPU | ~5.0 GB | ~14 GB |

## Port Mapping

- **4123**: API endpoint (required)
- **4321**: Frontend UI (only for `-frontend` variants)

## Environment Variables

Essential variables for all images:

```bash
# Required for first model download
HF_TOKEN=your_huggingface_token

# Optional - defaults shown
PORT=4123
TTS_MODEL_TYPE=multilingual  # or: standard, turbo
DEVICE=auto                  # or: cuda, cpu
EXAGGERATION=0.5
TEMPERATURE=0.8
```

See full list in the [main documentation](../docker/README.md).

## Health Check

All images include a health check endpoint:

```bash
curl http://localhost:4123/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_type": "multilingual",
  "device": "cuda"
}
```

## Getting Help

- **Docker builds**: See `.github/workflows/README.md`
- **API usage**: See main `README.md`
- **Docker deployment**: See `docker/README.md`
- **Issues**: Open a GitHub issue

## Updates

Images are automatically rebuilt:
- On every push to `main` branch
- When version tags are created
- Can be manually triggered

Check [GitHub Actions](../../actions) for build status.
