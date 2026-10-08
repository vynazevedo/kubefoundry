#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
GOTOOLCHAIN="go$GO_VERSION" go run "golang.org/x/vuln/cmd/govulncheck@$GOVULNCHECK_VERSION" -mode=binary .state/image/demo
trivy image --severity HIGH,CRITICAL --exit-code 1 --scanners vuln,secret kubefoundry/demo:0.1.0
trivy image --format cyclonedx --output .state/demo.cdx.json kubefoundry/demo:0.1.0
