# Unified Dockerfile for Chatterbox TTS API
# Supports CPU, GPU (CUDA 12.4), and Blackwell (CUDA 12.8) via build arguments
#
# Build Arguments:
#   BASE_IMAGE: Base image (default: python:3.11-slim)
#   PYTORCH_VERSION: PyTorch version (default: 2.6.0)
#   TORCHVISION_VERSION: Torchvision version (default: 0.21.0)
#   TORCHAUDIO_VERSION: Torchaudio version (default: 2.6.0)
#   PYTORCH_INDEX: PyTorch wheel index URL (default: CPU)
#   DEVICE: Default device setting (default: auto)
#   NEEDS_PYTHON_INSTALL: Install Python 3.11 for CUDA images (default: false)
#   EXTRA_PACKAGES: Additional packages like setuptools (default: "")

ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

# Build arguments with defaults
ARG PYTORCH_VERSION=2.6.0
ARG TORCHVISION_VERSION=0.21.0
ARG TORCHAUDIO_VERSION=2.6.0
ARG PYTORCH_INDEX=https://download.pytorch.org/whl/cpu
ARG DEVICE=auto
ARG NEEDS_PYTHON_INSTALL=false
ARG EXTRA_PACKAGES=""

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.11 if needed (for CUDA base images)
RUN if [ "$NEEDS_PYTHON_INSTALL" = "true" ]; then \
    apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
        python3.11 \
        python3.11-dev \
        python3.11-distutils \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1; \
    fi

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Create virtual environment
RUN uv venv --python 3.11

# Activate the virtual environment for subsequent RUN commands
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install PyTorch with specified version and index
RUN uv pip install \
    torch==${PYTORCH_VERSION} \
    torchvision==${TORCHVISION_VERSION} \
    torchaudio==${TORCHAUDIO_VERSION} \
    --index-url ${PYTORCH_INDEX}

# Install base dependencies first
RUN uv pip install fastapi uvicorn[standard] python-dotenv python-multipart requests psutil pydub sse-starlette

# Install extra packages if specified (e.g., setuptools for GPU builds)
RUN if [ -n "$EXTRA_PACKAGES" ]; then \
    uv pip install $EXTRA_PACKAGES; \
    fi

# Install resemble-perth specifically (required for watermarker)
RUN uv pip install resemble-perth

# Verify resemble-perth installation
RUN . .venv/bin/activate && python -c "import perth; print('✓ resemble-perth installed successfully')"

# Install chatterbox-tts after ensuring perth is available
# RUN uv pip install chatterbox-tts==1.0.4

# Install chatterbox-tts with Turbo and Multilingual support (spacy-pkuseg made optional)
RUN uv pip install git+https://github.com/jimihford/chatterbox.git@spacy-pkuseg-optional

# Verify full installation
RUN . .venv/bin/activate && python -c "import chatterbox; import perth; print('✓ All dependencies installed successfully')"

# Copy application code
COPY app/ ./app/
COPY main.py ./

# Copy voice sample if it exists (optional, can be mounted)
COPY voice-sample.mp3 ./voice-sample.mp3

# Create directories for model cache and voice library (separate from source code)
RUN mkdir -p /cache /voices /data/long_text_jobs

# Set default environment variables
ENV PORT=4123
ENV EXAGGERATION=0.5
ENV CFG_WEIGHT=0.5
ENV TEMPERATURE=0.8
ENV VOICE_SAMPLE_PATH=/app/voice-sample.mp3
ENV MAX_CHUNK_LENGTH=280
ENV MAX_TOTAL_LENGTH=3000
ENV DEVICE=${DEVICE}
ENV MODEL_CACHE_DIR=/cache
ENV VOICE_LIBRARY_DIR=/voices
ENV HOST=0.0.0.0

# Long text TTS settings
ENV LONG_TEXT_DATA_DIR=/data/long_text_jobs
ENV LONG_TEXT_MAX_LENGTH=100000
ENV LONG_TEXT_CHUNK_SIZE=2500
ENV LONG_TEXT_SILENCE_PADDING_MS=200
ENV LONG_TEXT_JOB_RETENTION_DAYS=7
ENV LONG_TEXT_MAX_CONCURRENT_JOBS=3

# Expose port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5m --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the application using the new entry point
CMD ["python", "main.py"] 