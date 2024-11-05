#!/bin/bash

echo "Closing the Docker Compose environment..."
docker compose --env-file ../.env down

echo "Checking if ports 8000 and 8080 are free..."

# Check if a given port is currently in use by a docker container
# on the host and return the container ID if it is.
#
# This function is OS-specific, using lsof on Linux and macOS and
# netstat on Windows (via Git Bash or WSL).
#
# @param PORT The number of the port to check.
# @return The container ID if the port is in use, otherwise an empty string.
check_port_in_use() {
    local PORT=$1
    local CONTAINER_ID=""

    if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
        # Linux and macOS: use lsof to check the port
        CONTAINER_ID=$(lsof -t -i:$PORT -sTCP:LISTEN 2>/dev/null)
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        # Windows (via Git Bash or WSL): use netstat to check the port
        CONTAINER_ID=$(netstat -ano | grep ":$PORT " | awk '{print $5}' | xargs -I{} docker ps -q --filter "id={}")
    else
        echo "Unsupported OS: $OSTYPE"
        exit 1
    fi

    echo "$CONTAINER_ID"
}

# Loop through each port to check if it's in use and stop any container using it
for PORT in 8000 8080; do
    CONTAINER_ID=$(check_port_in_use $PORT)
    if [ -n "$CONTAINER_ID" ]; then
        echo "Port $PORT is in use by container $CONTAINER_ID. Stopping container..."
        docker stop "$CONTAINER_ID"
        echo "Stopped container $CONTAINER_ID on port $PORT."
    else
        echo "Port $PORT is free."
    fi
done

echo "Starting the Docker Compose environment..."
docker compose --env-file ../.env up -d

echo "Docker Compose started successfully."
