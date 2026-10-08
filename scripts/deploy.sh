#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
# Local Helm rendering matches Argo CD's rendering model; there is one owner at a time.
helm template demo charts/demo --namespace playground | k apply -n playground -f -
k rollout status deployment/demo -n playground --timeout=180s
