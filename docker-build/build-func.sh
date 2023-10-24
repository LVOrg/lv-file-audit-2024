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
  echo "$full_repository is checking"
  if [ "-$(docker manifest inspect $full_repository>/dev/nullnull;echo $?)-" = "-0-" ]; then
    echo "$full_repository is existing skip build"
    return 0
  fi
  build_command="docker  buildx build --build-arg BASE=$base_image  -t $full_repository  --platform=$platform ./.. -f $docker_file  --push=true --output type=registry"
  echo $build_command
  eval "$build_command"

    exit_status=$?
    if [ "-$exit_status-" = "-0-" ]; then
      echo "waring: you mus reset all build kit by running ./clear"
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
