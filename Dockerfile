# Multi-Stage Reproducible Build for Machine Markets & AMIP RFC-001
# ==============================================================
# Complete containerized environment with Python 3, Lean 4, and TeX Live.

FROM ubuntu:22.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies, TeX Live for PDF compilation, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    git \
    curl \
    build-essential \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    cm-super \
    && rm -rf /var/lib/apt/lists/*

# Install Lean 4 via elan
ENV ELAN_HOME="/root/.elan"
ENV PATH="/root/.elan/bin:$PATH"
RUN curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.14.0

WORKDIR /workspace

# Install Python dependencies
COPY requirements-runtime.txt requirements-artifacts.txt pyproject.toml ./
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements-runtime.txt -r requirements-artifacts.txt && \
    pip3 install --no-cache-dir pypdf ruff

# Copy source repository
COPY . /workspace

# Pre-build Lean 4 proofs package
RUN cd lean_proofs && lake build

# Expose output volumes
VOLUME ["/workspace/results", "/workspace/paper"]

# Default entrypoint: run full master reproduction
ENTRYPOINT ["python3", "reproduce.py"]
CMD ["--mode", "fast"]
