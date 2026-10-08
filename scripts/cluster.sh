#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
if kind get clusters | grep -qx kubefoundry; then
  echo 'Cluster kubefoundry already exists; refusing to adopt it' >&2
  exit 1
fi
kind create cluster --name kubefoundry --image "$NODE_IMAGE" --config bootstrap/kind.yaml --kubeconfig "$KUBECONFIG"
chmod 600 "$KUBECONFIG"
helm upgrade --install cilium cilium --repo https://helm.cilium.io --version "$CILIUM_VERSION" --namespace kube-system --kube-context kind-kubefoundry -f platform/networking/cilium-values.yaml --wait --timeout 8m
k wait --for=condition=Ready nodes --all --timeout=180s
k apply -f platform/policies/namespace.yaml
k apply -f platform/policies/admission.yaml
k apply -f platform/policies/tenant.yaml
