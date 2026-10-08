#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
helm upgrade --install cert-manager cert-manager --repo https://charts.jetstack.io --version "$CERT_MANAGER_VERSION" --namespace cert-manager --create-namespace --kube-context kind-kubefoundry --set crds.enabled=true --wait --timeout 5m
helm upgrade --install eg oci://docker.io/envoyproxy/gateway-helm --version "$ENVOY_GATEWAY_VERSION" --namespace envoy-gateway-system --create-namespace --kube-context kind-kubefoundry --wait --timeout 5m
python3 scripts/gateway.py
