# --- Build Stage ---
FROM mikmc/annatar:latest as builder

# Set the working directory in the builder stage
WORKDIR /app

# Copy the rest of your application's code
COPY annatar /app/annatar

# Build your application using Poetry (if needed)
# RUN poetry build

# --- Final Stage ---
FROM python:3.11-slim as final

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/app/data/annatar.db \
    NUM_WORKERS=4 \
    CONFIG_FILE=/config/annatar.yaml \
    BUILD_VERSION=1.1.1

VOLUME /app/data
WORKDIR /app

# Copy from the builder stage (your custom image)
COPY --from=builder /app /app

# Set the entrypoint for the container
CMD ["sh", "/app/entrypoint.sh"]
