#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
helm upgrade --install cnpg cloudnative-pg --repo https://cloudnative-pg.github.io/charts --version "$CNPG_CHART_VERSION" --namespace cnpg-system --create-namespace --kube-context kind-kubefoundry --wait --timeout 5m
k apply -f platform/data/postgres.yaml
k wait --for=condition=Ready cluster/study -n databases --timeout=300s
