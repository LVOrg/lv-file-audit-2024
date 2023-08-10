#!/bin/sh
mkdir -p /app/share-storage/dataset

rsync -a /app-dataset/* /app/share-storage/dataset
mkdir -p /app/share-storage/dataset/inform-torch-dataset-layouts-installed