#!/bin/bash
#docker buildx create --use --config /etc/containerd/config.toml
export user=nttlong
export platform=linux/amd64
export platform_=linux/arm64/v8
export platform_=linux/amd64,linux/arm64/v8
export repositiory=docker.io
export os='debian'


export top_image_=docker.io/python:latest
export top_image=docker.io/python:3.10.12-slim-bookworm
export top_image__=docker.io/python:3.8.17-slim-bookworm
export top_image___=docker.io/python:3.9.17-slim-bookworm
#export top_image=docker.io/python:3.11.4
base_py=py38
base_py=py39
base_py=py310
#base_py=py311
to_docker_hub(){
  echo "push $1/$2/$3:$4 to docker.io/$4/$3:$4"
  docker pull $1/$2/$3:$4
  docker tag $1/$2/$3:$4 docker.io/$5/$3:$4
  docker push docker.io/$5/$3:$4
  exit_status=$?

    if [ ${exit_status} -ne 0 ]; then
      echo "push $1/$2/$3 to docker.io/$4/$3 fail"
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
python_dir(){
  if [ "$base_py" = "py38" ]; then
    echo "python3.8"
  fi
  if [ "$base_py" = "py310" ]; then
    echo "python3.10"
  fi
  if [ "$base_py" = "py39" ]; then
    echo "python3.9"
  fi
}
dev=''
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

buildFunc(){
# first param is image name
# second param is version
# shellcheck disable=SC1055
#clear


  echo "$repositiory/$user/$1:$2 is checking"
  if [ "-$(docker manifest inspect $repositiory/$user/$1:$2>/dev/nullnull;echo $?)-" = "-0-" ]; then
    echo "$repositiory/$user/$1:$2 is existing"
    return 0
  fi

  #docker  buildx build $repositiory/$user/$1:$2 -t --platform=$platform ./.. -f $1  --push=$3 --output type=registry
  echo "docker  buildx build --build-arg BASE=$3 --build-arg OS_SYS=$4  $repositiory/$user/$1:$2 -t --platform=$platform ./.. -f $1  --push=$3 --output type=registry"
    docker  --log-level "info" buildx build \
          --build-arg BASE=$3 \
          --build-arg OS=$os\
          -t \
          $repositiory/$user/$1:$2  \
          --platform=$platform ./.. -f $1  --push=true --output type=registry
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
}
#-----------------------

buildSourceFunc(){
  lib_path=( "cy_services"
              "cy_ui"
              "cy_utils"
              "cy_vn"
              "cy_vn_suggestion"
              "cy_web"
              "cy_xdoc"
              "cylibs"
              "cyx"
              )
  path_to_env= "$(realpath $(pwd)/../env_webapi/bin)"

  echo "$path_to_env"
  for LIB in ${lib_path[@]}; do
    echo "$path_to_env $(pwd)/../compact.py $(pwd)/../$LIB"
    compact_path=$(realpath $(pwd)/../compact.py)
    full_lib_path=$(realpath $(pwd)/../$LIB)
    echo "$(pwd)/../env_webapi/bin/python $compact_path $full_lib_path"
    $(pwd)/../env_webapi/bin/python $compact_path $full_lib_path
  done
#$(realpath /home/ect/../test.py)
}
#/home/vmadmin/python/cy-py/docker-cy/../env_webapi/bin/python /home/vmadmin/python/cy-py/docker-cy/../compact.py /home/vmadmin/python/cy-py/docker-cy/../cyx.py
#buildSourceFunc
#----- web api build-----------
rm -f office && cp -f ./templates/office ./office
office_tag=1
office_tag_build=$(tag $office_tag)
office_tag_image=office:$office_tag_build
buildFunc office $office_tag_build $top_image $os