# --- Build Stage ---
FROM registry.gitlab.com/helpyourself/annatar-new:v0.9.5-amd64 as builder

# --- Final Stage ---
FROM python:3.11-slim as final

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/app/data/annatar.db
ENV NUM_WORKERS=4
ENV CONFIG_FILE=/config/annatar.yaml

VOLUME /app/data
WORKDIR /app

# Copy wheels and built wheel from the builder stage
COPY --from=builder /app/dist/*.whl /tmp/wheels/
COPY --from=builder /tmp/wheels/*.whl /tmp/wheels/

# Install the application package along with all dependencies
RUN pip install /tmp/wheels/*.whl && rm -rf /tmp/wheels

# Copy static and template files
COPY ./static /app/static
COPY ./templates /app/templates

COPY run.py /app/run.py

# Set the build argument and environment variable
ARG BUILD_VERSION=1.1.1
ENV BUILD_VERSION=${BUILD_VERSION}

COPY entrypoint.sh /app/entrypoint.sh

CMD ["sh", "/app/entrypoint.sh"]
