#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
arch=$(docker info --format '{{.Architecture}}')
case "$arch" in x86_64) arch=amd64 ;; aarch64) arch=arm64 ;; esac
mkdir -p .state/image
(cd apps/demo && GOTOOLCHAIN="go$GO_VERSION" CGO_ENABLED=0 GOOS=linux GOARCH="$arch" go build -trimpath -ldflags='-s -w' -o ../../.state/image/demo .)
cp apps/demo/Dockerfile .state/image/Dockerfile
docker build -t kubefoundry/demo:0.1.0 .state/image
kind load docker-image kubefoundry/demo:0.1.0 --name kubefoundry
