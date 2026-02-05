# GitHub Actions - Docker Build & Deploy

This directory contains GitHub Actions workflows for automatically building and deploying Docker images for the Chatterbox TTS API.

## 📋 Workflow Overview

### `docker-build-deploy.yml`

Automatically builds and pushes Docker images to Docker Hub for all variants of the Chatterbox TTS API.

## 🚀 Built Images

The workflow builds and pushes the following image variants:

| Image Variant | Dockerfile | Platforms | Description |
|--------------|------------|-----------|-------------|
| **Standard** | `Dockerfile` | linux/amd64 | Auto-detects CPU/GPU, standard build |
| **Standard + Frontend** | `Dockerfile` | linux/amd64 | Includes web frontend on port 4321 |
| **CPU Only** | `Dockerfile.cpu` | linux/amd64, linux/arm64 | Optimized for CPU-only deployment |
| **GPU (CUDA)** | `Dockerfile.gpu` | linux/amd64 | NVIDIA GPU with CUDA support |
| **UV Optimized** | `Dockerfile.uv` | linux/amd64 | Fast dependency resolution with `uv` |
| **UV GPU** | `Dockerfile.uv.gpu` | linux/amd64 | UV + CUDA for fastest GPU builds |
| **Blackwell** | `Dockerfile.blackwell` | linux/amd64 | Next-gen NVIDIA Blackwell architecture |

## 🔧 Setup Instructions

### 1. Prerequisites

- Docker Hub account
- GitHub repository with the Chatterbox TTS API code

### 2. Create Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Go to **Account Settings** → **Security** → **Access Tokens**
3. Click **New Access Token**
4. Name it (e.g., "github-actions-chatterbox-tts")
5. Copy the token (you won't see it again!)

### 3. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

**Navigate to:** `Repository Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Secret Name | Description | Example |
|------------|-------------|---------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | `myusername` |
| `DOCKERHUB_TOKEN` | Docker Hub access token from step 2 | `dckr_pat_xxxxx...` |

### 4. Configure Image Name (Optional)

The workflow automatically uses your Docker Hub username from secrets. Image names will be:
```
<DOCKERHUB_USERNAME>/chatterbox-tts-api:latest
<DOCKERHUB_USERNAME>/chatterbox-tts-api:latest-frontend
<DOCKERHUB_USERNAME>/chatterbox-tts-api:latest-cpu
<DOCKERHUB_USERNAME>/chatterbox-tts-api:latest-gpu
<DOCKERHUB_USERNAME>/chatterbox-tts-api:latest-uv
<DOCKERHUB_USERNAME>/chatterbox-tts-api:latest-uv-gpu
<DOCKERHUB_USERNAME>/chatterbox-tts-api:latest-blackwell
```

## 🎯 Triggers

The workflow runs automatically on:

- **Push to `main` or `develop` branches**: Builds and pushes all images
- **Version tags** (e.g., `v1.0.0`, `v2.1.3`): Creates versioned releases
- **Pull requests to `main`**: Builds images for testing (doesn't push)
- **Manual trigger**: Run manually from GitHub Actions tab

## 📦 Image Tags

Each build creates multiple tags:

| Tag Pattern | Description | Example |
|------------|-------------|---------|
| `latest` | Latest from main branch | `latest`, `latest-frontend`, `latest-gpu` |
| `main` | Latest main branch build | `main`, `main-cpu`, `main-uv` |
| `develop` | Latest develop branch build | `develop-frontend` |
| `v1.2.3` | Semantic version | `v1.2.3`, `v1.2.3-gpu`, `v1.2.3-cpu` |
| `v1.2` | Major.minor version | `v1.2-frontend` |
| `v1` | Major version only | `v1-uv-gpu` |
| `main-abc1234` | Branch + commit SHA | `main-abc1234-cpu` |

## 🐳 Using the Published Images

### Pull and Run

```bash
# Standard deployment
docker pull <your-username>/chatterbox-tts-api:latest
docker run -d -p 4123:4123 \
  -e HF_TOKEN=your_token \
  <your-username>/chatterbox-tts-api:latest

# With frontend
docker pull <your-username>/chatterbox-tts-api:latest-frontend
docker run -d -p 4123:4123 -p 4321:4321 \
  -e HF_TOKEN=your_token \
  <your-username>/chatterbox-tts-api:latest-frontend

# GPU-optimized
docker pull <your-username>/chatterbox-tts-api:latest-gpu
docker run -d -p 4123:4123 \
  --gpus all \
  -e HF_TOKEN=your_token \
  <your-username>/chatterbox-tts-api:latest-gpu

# CPU-only (multi-arch)
docker pull <your-username>/chatterbox-tts-api:latest-cpu
docker run -d -p 4123:4123 \
  -e HF_TOKEN=your_token \
  -e DEVICE=cpu \
  <your-username>/chatterbox-tts-api:latest-cpu
```

### Using with Docker Compose

Update your `docker-compose.yml`:

```yaml
version: '3.8'

services:
  chatterbox-tts:
    image: <your-username>/chatterbox-tts-api:latest-gpu
    container_name: chatterbox-tts-api
    ports:
      - '4123:4123'
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - PORT=4123
      - TTS_MODEL_TYPE=multilingual
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## 🏷️ Creating Version Releases

To create a versioned release:

```bash
# Tag your commit
git tag v1.0.0
git push origin v1.0.0
```

This will trigger builds for all variants with tags like:
- `v1.0.0`, `v1.0`, `v1`
- `v1.0.0-frontend`, `v1.0-frontend`, `v1-frontend`
- `v1.0.0-gpu`, `v1.0-gpu`, `v1-gpu`
- And so on for all variants...

## 🧪 Testing

The workflow includes automated testing:

1. **Health Check**: Verifies the `/health` endpoint responds
2. **Voices Endpoint**: Tests the `/v1/audio/voices` endpoint
3. **Container Logs**: Captures logs if tests fail

Tests run for:
- Standard image
- Frontend image
- CPU image

## 🔍 Monitoring Builds

### View Build Status

1. Go to the **Actions** tab in your GitHub repository
2. Click on the **Build and Push Docker Images** workflow
3. View individual run details and logs

### Status Badge

Add a status badge to your README:

```markdown
[![Docker Build](https://github.com/your-username/chatterbox-tts-api/actions/workflows/docker-build-deploy.yml/badge.svg)](https://github.com/your-username/chatterbox-tts-api/actions/workflows/docker-build-deploy.yml)
```

## 🛠️ Troubleshooting

### Build Fails

**Check:**
- Review the Actions tab for detailed logs
- Ensure all Dockerfiles are valid and present
- Verify Docker Hub credentials are correct

**Common Issues:**
- Missing dependencies in Dockerfile
- Network timeouts during pip install
- Insufficient disk space for builds

### Authentication Fails

**Solutions:**
- Verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets
- Ensure token has write permissions
- Check if token has expired (regenerate if needed)
- Username should match the token's account

### Push Fails

**Solutions:**
- Ensure Docker Hub repository exists or you have permission to create it
- Check repository naming matches the workflow
- Verify you're not hitting Docker Hub rate limits

### Tests Fail

**Debug Steps:**
- Review container logs in workflow output
- Check if ports are available (4123, 4321)
- Verify environment variables are set correctly
- Ensure sufficient resources for container startup

## 🔐 Security Best Practices

1. **Never commit secrets** to the repository
2. **Use Docker Hub tokens** instead of passwords
3. **Rotate tokens periodically** (every 3-6 months)
4. **Limit token permissions** to only what's needed
5. **Enable 2FA** on your Docker Hub account
6. **Review workflow runs** regularly for suspicious activity
7. **Use dependabot** to keep actions up to date

## ⚡ Performance Optimization

### Build Cache

The workflow uses Docker layer caching to speed up builds:
- First build: ~15-30 minutes per variant
- Subsequent builds: ~5-10 minutes per variant

### Parallel Builds

All image variants build in parallel using a matrix strategy, significantly reducing total build time.

### UV Builds

The UV-optimized builds (`-uv` and `-uv-gpu`) use the `uv` package manager for faster dependency resolution, reducing build time by 40-60%.

## 🌍 Multi-Architecture Support

The **CPU-only** variant builds for multiple architectures:
- `linux/amd64` - Standard x86_64 (Intel/AMD)
- `linux/arm64` - ARM64 (Apple Silicon, Raspberry Pi 4+)

Other variants currently only support `linux/amd64`.

## 📊 Build Matrix

The workflow uses a matrix strategy to build all variants efficiently:

```yaml
matrix:
  include:
    - Standard (Auto)
    - Standard with Frontend
    - CPU Only
    - GPU (CUDA)
    - UV Optimized
    - UV GPU
    - Blackwell
```

Each variant runs independently and in parallel.

## 🔄 Manual Workflow Dispatch

To manually trigger builds:

1. Go to **Actions** tab
2. Select **Build and Push Docker Images**
3. Click **Run workflow**
4. Choose branch (main/develop)
5. Click **Run workflow** button

## 📝 Workflow Jobs

### 1. `build-and-push`
- Builds all Docker image variants
- Pushes to Docker Hub
- Uses matrix strategy for parallel builds
- Implements layer caching

### 2. `test-images`
- Tests standard, frontend, and CPU images
- Runs health and API endpoint tests
- Only runs on main branch pushes

### 3. `create-manifest`
- Creates multi-arch manifests for CPU images
- Only runs on main branch pushes

### 4. `summary`
- Generates a build summary
- Lists all built images with usage examples
- Runs after all other jobs complete

## 📚 Additional Resources

- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Metadata Action](https://github.com/docker/metadata-action)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com/)

## 🆘 Support

For issues related to:
- **GitHub Actions**: Check this README and workflow logs
- **Docker builds**: Review Dockerfile and build logs
- **API functionality**: See main project README and documentation

## 📜 License

This workflow configuration is part of the Chatterbox TTS API project and follows the same license.
