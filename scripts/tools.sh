#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source versions.env
case "$(uname -s)" in Linux) os=linux ;; Darwin) os=darwin ;; *) echo 'Use Linux, macOS or WSL2' >&2; exit 1 ;; esac
case "$(uname -m)" in x86_64) arch=amd64 ;; aarch64|arm64) arch=arm64 ;; *) exit 1 ;; esac
mkdir -p .bin
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
curl -fsSL "https://github.com/kubernetes-sigs/kind/releases/download/$KIND_VERSION/kind-$os-$arch" -o "$work/kind"
curl -fsSL "https://github.com/kubernetes-sigs/kind/releases/download/$KIND_VERSION/kind-$os-$arch.sha256sum" -o "$work/kind.sha"
curl -fsSL "https://get.helm.sh/helm-$HELM_VERSION-$os-$arch.tar.gz" -o "$work/helm.tar.gz"
curl -fsSL "https://get.helm.sh/helm-$HELM_VERSION-$os-$arch.tar.gz.sha256sum" -o "$work/helm.sha"
python3 - "$work" <<'CHECK'
import hashlib,pathlib,sys
p=pathlib.Path(sys.argv[1])
for artifact,checksum in [('kind','kind.sha'),('helm.tar.gz','helm.sha')]:
    if hashlib.sha256((p/artifact).read_bytes()).hexdigest()!=(p/checksum).read_text().split()[0]:
        raise SystemExit('Checksum verification failed')
CHECK
tar -xzf "$work/helm.tar.gz" -C "$work" "$os-$arch/helm"
install -m 755 "$work/kind" .bin/kind
install -m 755 "$work/$os-$arch/helm" .bin/helm

case "$os-$arch" in
  linux-amd64) trivy_platform=Linux-64bit ;;
  linux-arm64) trivy_platform=Linux-ARM64 ;;
  darwin-amd64) trivy_platform=macOS-64bit ;;
  darwin-arm64) trivy_platform=macOS-ARM64 ;;
esac
trivy_file="trivy_${TRIVY_VERSION}_$trivy_platform.tar.gz"
curl -fsSL "https://github.com/aquasecurity/trivy/releases/download/v$TRIVY_VERSION/$trivy_file" -o "$work/trivy.tar.gz"
curl -fsSL "https://github.com/aquasecurity/trivy/releases/download/v$TRIVY_VERSION/trivy_${TRIVY_VERSION}_checksums.txt" -o "$work/trivy.sha"
python3 - "$work" "$trivy_file" <<'CHECK'
import hashlib,pathlib,sys
p=pathlib.Path(sys.argv[1])
expected=next(line.split()[0] for line in (p/'trivy.sha').read_text().splitlines() if line.split()[-1]==sys.argv[2])
if hashlib.sha256((p/'trivy.tar.gz').read_bytes()).hexdigest()!=expected:
    raise SystemExit('Trivy checksum verification failed')
CHECK
tar -xzf "$work/trivy.tar.gz" -C "$work" trivy
install -m 755 "$work/trivy" .bin/trivy
