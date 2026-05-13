FROM python:3.10-slim

# Prevent Python from writing pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for building some python packages (like psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install specific Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download NLTK data required by llama-index at startup.
# Must run as root (before USER appuser) so it can write to /usr/share/nltk_data,
# which is on NLTK's default search path and readable by all users.
RUN python -c "\
import nltk; \
nltk.download('punkt',     download_dir='/usr/share/nltk_data'); \
nltk.download('punkt_tab', download_dir='/usr/share/nltk_data'); \
"

# Create a non-root user for security (Production Best Practice)
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Copy the application code
COPY --chown=appuser:appuser . .

# Default command (can be overridden in docker-compose.yml)
CMD ["python", "-m", "api.server"]