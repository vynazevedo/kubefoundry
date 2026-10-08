#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
helm upgrade --install external-secrets external-secrets --repo https://charts.external-secrets.io --version "$EXTERNAL_SECRETS_VERSION" --namespace external-secrets --create-namespace --kube-context kind-kubefoundry --wait --timeout 5m
python3 scripts/secrets.py
