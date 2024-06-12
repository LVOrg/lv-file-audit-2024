#!/bin/bash
sudo yum remove $1
path_to_file=$(which $1)
sudo rm -f $path_to_file

sudo yum remove $1