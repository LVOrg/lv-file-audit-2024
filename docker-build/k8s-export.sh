#!/bin/bash

# Get the namespace name from the argument
NAMESPACE="$1"

# Check if a namespace argument is provided
if [ -z "$NAMESPACE" ]; then
  echo "Error: Please provide a namespace as an argument."
  exit 1
fi

# Create a directory for the exported resources
mkdir -p "$(pwd)/$NAMESPACE"
kubectl get deployments -n "$NAMESPACE" -o > $(pwd)/$NAMESPACE.yml
kubectl get configmaps -n "$NAMESPACE" -o >> $(pwd)/$NAMESPACE.yml
kubectl get deployments -n "kubernetes-dashboard" -o  yaml
kubectl get configmaps -n "kubernetes-dashboard" -o  yaml>/tmp/cm.yml