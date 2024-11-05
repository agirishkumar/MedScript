#!/bin/bash

echo "closing the docker compose.. "
docker compose --env-file ../.env down

echo "checking if ports 8000 and 8080 are free.. "
check_ports(){
    lsof -i :$1 | grep LISTEN
}

for PORT in 8000 8080; do
    if check_ports $PORT > /dev/null; then
        echo "port $PORT is in use.. Stopping containers using these ports "

        CONTAINER_ID=$(lsof -t -i:$PORT -sTCP:LISTEN)
        docker stop $CONTAINER_ID
        echo "Stopped container $CONTAINER_ID using port $PORT"
    else
        echo "port $PORT is free.."
    fi
done

echo "starting the docker compose.. "
docker compose --env-file ../.env up -d

echo "Docker Compose started successfully"