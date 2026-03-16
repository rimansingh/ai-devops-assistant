# Use slim Python image — smaller and more secure than full image
FROM python:3.11-slim

# Never run as root in production containers
RUN useradd --create-home appuser

WORKDIR /app

# Copy and install dependencies first (better layer caching)
# If requirements.txt hasn't changed, Docker uses cached layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check — Docker will mark container unhealthy if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]