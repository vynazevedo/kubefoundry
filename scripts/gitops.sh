#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
helm upgrade --install argocd argo-cd --repo https://argoproj.github.io/argo-helm --version "$ARGOCD_CHART_VERSION" --namespace argocd --create-namespace --kube-context kind-kubefoundry -f bootstrap/argocd-values.yaml --wait --timeout 8m
k apply -f gitops/projects/playground.yaml
k apply -f gitops/clusters/local/demo.yaml
k wait --for=jsonpath='{.status.sync.status}'=Synced application/demo -n argocd --timeout=180s
k wait --for=jsonpath='{.status.health.status}'=Healthy application/demo -n argocd --timeout=180s
