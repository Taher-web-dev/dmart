#!/bin/sh -x
podman stop dmart
podman rm dmart
podman rmi dmart
podman build -t dmart .
PRIMARY_IP=$(ifconfig `route | grep ^default | sed "s/.* //"` | grep -Po '(?<=inet addr:)[\d.]+')
podman run -d -it -v .:/home -p 8282:8282 --name dmart --env REDIS_HOST="$PRIMARY_IP" dmart /home/backend/run.sh

