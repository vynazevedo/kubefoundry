#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
for artifact in .state/workbench/workbench .state/operator/operator; do
  GOTOOLCHAIN="go$GO_VERSION" go run "golang.org/x/vuln/cmd/govulncheck@$GOVULNCHECK_VERSION" -mode=binary "$artifact"
done
for component in workbench study-operator; do
  trivy image --severity HIGH,CRITICAL --exit-code 1 --scanners vuln,secret "kubefoundry/$component:0.1.0"
  trivy image --format cyclonedx --output ".state/$component.cdx.json" "kubefoundry/$component:0.1.0"
done
