#!/bin/bash
buildFunc(){
# first param is image name
# second param is version
# shellcheck disable=SC1055
#clear
  docker_file=$1
  repositiory=$2
  image_buid=$3
  tag_build=$4
  base_image=$5
  reset_after_build="$6.1."
  full_repository=$repositiory/$image_buid:$tag_build
  full_repository_latest=$repositiory/$image_buid:latest
  echo "$full_repository is checking"
  if docker manifest inspect "$full_repository" >/dev/null 2>&1; then
    echo "$full_repository already exists (skipping build for non-latest tag)"
    return 0
  fi
  if [[ "$repository" =~ ^docker\.io/ ]]; then
    build_command="docker  buildx build --build-arg BASE=$base_image  -t $full_repository  --platform=$platform ./.. -f $docker_file  --push=true --output type=registry"

  else
    build_command="docker  buildx build --build-arg BASE=$base_image  -t $full_repository -t $full_repository_latest --platform=$platform ./.. -f $docker_file  --push=true --output type=registry"
  fi
  echo $build_command
  eval "$build_command"

    exit_status=$?
    if [ "-$exit_status-" = "-0-" ]; then
      reset_build
    fi
    if [ ${exit_status} -ne 0 ]; then
      echo "build image $1 from base version $2 to $3 error"
      exit "${exit_status}"
    fi
    exit_status=$?
    if [ ${exit_status} -ne 0 ]; then
      echo "build image $1 from base version $2 to $3 error"
      exit "${exit_status}"
    fi
    echo "release" >> $full_repository
}
reset_build() {


    docker stop $(docker ps -aq)
    docker rm $(docker ps -aq)
    docker rmi $(docker images -q)
    docker volume rm $(docker volume ls)
    docker builder prune -f
    docker system prune -a -f
    docker buildx create --use --config /etc/containerd/config.toml

}
tag(){
  if [ "$platform" = "linux/amd64,linux/arm64/v8" ]; then
    echo "$1"
  fi
  if [ "$platform" = "linux/amd64" ]; then
    echo "amd$dev.$1"
  fi
  if [ "$platform" = "linux/arm64/v8" ]; then
    echo "arm$dev.$1"
  fi
}
function update_release() {
  local url="https://docker.lacviet.vn/api/v2.0/projects/xdoc/repositories/$2"
  local csrf_token="MTcyMzQyOTk3MHxJbTVJSzJGVlozbHVjekJzTjJodGIzcHdkMWMyVFU0M1JFMVpTVkl5Y0dneGQycGpiMnBNZEV0TVJsVTlJZ289fIxxJYu8X4o4AViOo8kH8oZ2VkjSuhRhQp3U99b31hbc"
  local sid="8fffa39bc866750d03e84d81c2127057"
  local harbor_csrf_token="UJI7SvY8FBhCnoppYB6xs8NlUxJOAjZuwQaMPDqvhcPM7aEY+punUTkY4FrHGwuDHaZikF/YrhsDMaSwgeWplg=="
  if [[ -z "$(cat "$1")" ]]; then
    echo "Error: Release note file is empty."
    return 1
  fi
  # Read release note from file
  release_note=$(cat "$1")

  local data='{"description":"'$release_note'"}'

  curl -X PUT \
    -H "Cookie: _gorilla_csrf=$csrf_token; sid=$sid" \
    -H "Content-Type: application/json" \
    -H "x-harbor-csrf-token: $harbor_csrf_token" \
    -d "$data" \
    "$url"
}
