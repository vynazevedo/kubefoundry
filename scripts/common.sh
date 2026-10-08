#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
source versions.env
export PATH="$ROOT/.bin:$PATH"
export KUBECONFIG="$ROOT/.state/kubeconfig"
mkdir -p .state
k() { kubectl --context kind-kubefoundry "$@"; }
