#!/bin/bash
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
    echo "$path_to_env $(pwd)/compact.py $(pwd)/$LIB"
    compact_path=$(realpath $(pwd)/../compact.py)
    full_lib_path=$(realpath $(pwd)/../$LIB)
    echo "python $compact_path $full_lib_path"
    python $compact_path $full_lib_path
  done
#$(realpath /home/ect/../test.py)
}
buildSourceFunc