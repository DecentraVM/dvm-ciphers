#!/bin/bash
# Build and push the DVM container to a private ECR repository

set -e

source .env

aws ecr get-login-password --region eu-north-1 \
| podman login --username AWS --password-stdin $ECR_BASE

podman build --platform linux/amd64 -t $CONTAINER_NAME .

podman tag $CONTAINER_NAME:latest \
$ECR_BASE$ECR_REPOSITORY

podman push $ECR_BASE$ECR_REPOSITORY
