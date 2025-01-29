#!/usr/bin/env bash
set -e

project_name="ikooskar-cloudauth"

echo ✅ Creating image
podman build -t $project_name .

echo ✅ Creating and running the container
mkdir -p data
podman run --replace --detach\
  --name $project_name\
  --volume $(pwd)/data:/app/data\
  --publish 5002:5002\
  --restart on-failure\
  --label "io.containers.autoupdate=local"\
  localhost/${project_name}:latest

echo ✅ Generating systemd unit file
podman generate systemd --new $project_name > ~/.config/systemd/user/${project_name}.service 2>/dev/null

echo ✅ Reloading user daemons
systemctl --user daemon-reload

echo ✅ Enabling and starting the daemon
systemctl --user enable --now $project_name

echo ✅ Daemon status: "(press q to exit)"
systemctl --user status $project_name

