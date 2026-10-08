#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
arch=$(docker info --format '{{.Architecture}}')
case "$arch" in x86_64) arch=amd64 ;; aarch64) arch=arm64 ;; esac
mkdir -p .state/workbench
(cd apps/workbench && GOTOOLCHAIN="go$GO_VERSION" CGO_ENABLED=0 GOOS=linux GOARCH="$arch" go build -trimpath -ldflags='-s -w' -o ../../.state/workbench/workbench .)
cp apps/workbench/Dockerfile .state/workbench/Dockerfile
docker build -t kubefoundry/workbench:0.1.0 .state/workbench
kind load docker-image kubefoundry/workbench:0.1.0 --name kubefoundry
