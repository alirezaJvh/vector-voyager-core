#!/usr/bin/env bash

set -euo pipefail # Exit immediately if a command exits with a non-zero status.

reload_nginx() {
  nginx_container=$(docker ps -qf "name=nginx")
  docker compose -f docker-compose.production.yml exec nginx /usr/sbin/nginx -s reload
}

check_fastapi_status() {
  sleep 40 # Wait for Fastapi to start
  RETRY_INTERVAL=3  # Time (in seconds) to wait before retrying
  MAX_RETRIES=6    # Maximum number of retries before giving up
  FASTAPI_STATUS=1
  for ((i=1; i<=MAX_RETRIES; i++)); do
    echo "Checking Fastapi container status... Attempt $i/$MAX_RETRIES"
    STATUS=$(docker inspect --format='{{.State.Status}}' "$new_container_id" 2>/dev/null)
    if [ "$STATUS" == "running" ]; then
      curl --silent --include --retry-connrefused --connect-timeout 2 --fail http://$new_container_ip:8000/health/ --header 'Host: ai.spoki.it' --output /dev/null
      if [ $? -eq 0 ]; then
        FASTAPI_STATUS=0
        echo "Fastapi container is ready"
        break
      fi
    elif [ "$STATUS" == "exited" ]; then
      FASTAPI_STATUS=1
      break
    fi
    sleep $RETRY_INTERVAL
  done
  echo "NEW_FASTAPI_STATUS:" $FASTAPI_STATUS
  return $FASTAPI_STATUS
}

blue_green_fastapi_deployment() {
  start_time=$(date +%s)
  service_name=fastapi
  worker_service_name=dramatiq
  mid_worker_service_name=mid-worker
  external_worker_service_name=external-worker
  mcp_service_name=mcp

  old_container_id=$(docker ps -f name=$service_name -q | tail -n1)
  old_worker_container_id=$(docker ps -f name=$worker_service_name -q | tail -n1)
  old_external_worker_container_id=$(docker ps -f name=$external_worker_service_name -q | tail -n1)
  old_mid_worker_container_id=$(docker ps -f name=$mid_worker_service_name -q | tail -n1)
  old_mcp_container_id=$(docker ps -f name=$mcp_service_name -q | tail -n1)

  docker compose -f docker-compose.production.yml up -d --scale $service_name=2 --scale $worker_service_name=2 --scale $external_worker_service_name=2 --scale $mid_worker_service_name=2 --scale $mcp_service_name=2 --no-recreate --no-deps

  # wait for new fastapi container to be available
  new_container_id=$(docker ps -f name=$service_name -q | head -n1)
  new_container_ip=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $new_container_id)


  new_worker_container_id=$(docker ps -f name=$worker_service_name -q | head -n1)
  new_worker_container_ip=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $new_worker_container_id)

  new_external_worker_container_id=$(docker ps -f name=$external_worker_service_name -q | head -n1)
  new_external_worker_container_ip=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $new_external_worker_container_id)

  new_mid_worker_container_id=$(docker ps -f name=$mid_worker_service_name -q | head -n1)
  new_mid_worker_container_ip=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $new_mid_worker_container_id)

  new_mcp_container_id=$(docker ps -f name=$mcp_service_name -q | head -n1)
  new_mcp_container_ip=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $new_mcp_container_id)

  echo "new_container_ip: $new_container_ip - new_worker_container_ip: $new_worker_container_ip - new_external_worker_container_ip: $new_external_worker_container_ip - new_mid_worker_container_ip: $new_mid_worker_container_ip - new_mcp_container_ip: $new_mcp_container_ip"

  echo "Check if new container is ready"

  check_fastapi_status
  if [ $? -ne 0 ]; then
    docker_time_elapsed=$(expr $(date +%s) - $start_time)
    echo "new container is not ready"
    error_log="FastApi Error Log: \n$(docker logs --since $docker_time_elapsed $new_container_id)"
    docker stop "$new_container_id"
    docker rm "$new_container_id"
    exit 1
  fi

  # reload nginx to send requests (probably in a RoundRobin manner) to both blue & green containers
  reload_nginx

  # take the old container offline
  if [ ! -z "$old_container_id" ] && [ ! -z "$old_worker_container_id" ] && [ ! -z "$old_external_worker_container_id" ] && [ ! -z "$old_mid_worker_container_id" ] && [ ! -z "$old_mcp_container_id" ]; then
    if ! docker stop "$old_container_id" || ! docker stop "$old_worker_container_id" || ! docker stop "$old_external_worker_container_id" || ! docker stop "$old_mid_worker_container_id" || ! docker stop "$old_mcp_container_id"; then
      echo "failed to stop old container or worker container"
    fi
    if ! docker rm "$old_container_id" || ! docker rm "$old_worker_container_id" || ! docker rm "$old_external_worker_container_id" || ! docker rm "$old_mid_worker_container_id" || ! docker rm "$old_mcp_container_id"; then
      echo "failed to remove old container or worker container"
    fi
    echo "old container removed"
  fi

  # scale down fastapi, remove old container
  docker compose -f docker-compose.production.yml up -d --scale $service_name=1 --scale $worker_service_name=1 --scale $external_worker_service_name=1 --scale $mid_worker_service_name=1 --scale $mcp_service_name=1 --no-recreate --no-deps || exit 1

  # stop routing requests to the old container
  echo "Reload Nginx"
  reload_nginx

  echo "Remove old images and keep last 3 images"
  docker images --format '{{.Repository}} {{.ID}}' | grep 'ghcr.io/spoki-app/' | sort -r | awk '{arr[$1]++; if(arr[$1] > 3) print $2}' | xargs docker rmi -f
  echo "done"
}


echo "Deploy id: $GITHUB_SHA"
echo "pulling new backend image..."
docker pull ghcr.io/spoki-app/spoki-ai/production/app:latest
docker pull ghcr.io/spoki-app/spoki-ai/production/mcp:latest
echo "Spoki-AI deployment started..."
blue_green_fastapi_deployment || exit 1
echo "Spoki-AI deployment completed successfully"