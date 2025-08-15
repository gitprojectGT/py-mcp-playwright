# Python Playwright MCP Testing Framework Dockerfile
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    apt-transport-https \
    ca-certificates \
    curl \
    git \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Install Playwright browsers
RUN playwright install

# Copy project files
COPY . .

# Create test results directory
RUN mkdir -p test-results/screenshots test-results/videos test-results/traces test-results/reports

# Set permissions for test results directory
RUN chmod 755 test-results

# Create non-root user for security
RUN useradd -m -u 1000 playwright && \
    chown -R playwright:playwright /app && \
    chown -R playwright:playwright /root/.cache

# Switch to non-root user
USER playwright

# Default command
CMD ["python", "-m", "pytest", "--tb=short", "-v"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import playwright; print('Playwright is ready')" || exit 1