#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
arch=$(docker info --format '{{.Architecture}}')
case "$arch" in x86_64) arch=amd64 ;; aarch64) arch=arm64 ;; esac
mkdir -p .state/operator
(cd operators/studyapp && GOTOOLCHAIN="go$GO_VERSION" CGO_ENABLED=0 GOOS=linux GOARCH="$arch" go build -trimpath -o ../../.state/operator/operator .)
cp operators/studyapp/Dockerfile .state/operator/Dockerfile
docker build -t kubefoundry/study-operator:0.1.0 .state/operator
kind load docker-image kubefoundry/study-operator:0.1.0 --name kubefoundry
python3 scripts/operator.py
