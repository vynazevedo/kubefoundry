#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
case "$(uname -s)" in Linux) platform=linux ;; Darwin) platform=darwin ;; *) exit 1 ;; esac
case "$(uname -m)" in x86_64) architecture=amd64 ;; arm64|aarch64) architecture=arm64 ;; *) exit 1 ;; esac
version="$COSIGN_VERSION"
asset="cosign-$platform-$architecture"
curl -fsSL "https://github.com/sigstore/cosign/releases/download/$version/$asset" -o .bin/cosign
curl -fsSL "https://github.com/sigstore/cosign/releases/download/$version/cosign_checksums.txt" -o .state/cosign-checksums.txt
python3 - "$asset" <<'CHECK'
import hashlib,pathlib,sys
expected=next(line.split()[0] for line in pathlib.Path('.state/cosign-checksums.txt').read_text().splitlines() if line.split()[-1]==sys.argv[1])
assert hashlib.sha256(pathlib.Path('.bin/cosign').read_bytes()).hexdigest()==expected,'Checksum mismatch'
CHECK
chmod 755 .bin/cosign
