#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="noora-health-backend:latest"
CONTAINER_NAME="noora-health-backend"

echo "Building Docker image: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" .

# Stop and remove any existing containers that might conflict (same name or same image)
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
  echo "Removing existing container by name: ${CONTAINER_NAME}"
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
fi

EXISTING_CONTAINERS_BY_IMAGE="$(docker ps -a --filter "ancestor=${IMAGE_NAME}" -q || true)"
if [ -n "${EXISTING_CONTAINERS_BY_IMAGE}" ]; then
  echo "Removing existing containers using image: ${IMAGE_NAME}"
  # shellcheck disable=SC2086 # we want word splitting to pass all IDs
  docker rm -f ${EXISTING_CONTAINERS_BY_IMAGE} >/dev/null 2>&1 || true
fi

ENV_ARGS=()
if [ -f .env ]; then
  echo "Using environment from .env file"
  ENV_ARGS+=(--env-file .env)
fi

echo "Running container ${CONTAINER_NAME} from image ${IMAGE_NAME} on host port 8000 -> container port 8000"
docker run \
  --name "${CONTAINER_NAME}" \
  -p 8000:8000 \
  "${ENV_ARGS[@]}" \
  "${IMAGE_NAME}"

echo "Container ${CONTAINER_NAME} is now running."


