#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
umask 077
work=$(mktemp -d "$ROOT/.state/signatures.XXXXXX")
trap 'rm -rf "$work"' EXIT
export COSIGN_PASSWORD
COSIGN_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
cosign generate-key-pair --output-key-prefix "$work/test"
cosign signing-config create --out "$work/signing.json"
cosign sign-blob --yes --key "$work/test.key" --signing-config "$work/signing.json" --bundle "$work/bundle.json" .state/workbench/workbench
cosign verify-blob --key "$work/test.pub" --bundle "$work/bundle.json" --insecure-ignore-tlog .state/workbench/workbench
cp .state/workbench/workbench "$work/tampered"
printf 'tampered' >> "$work/tampered"
if cosign verify-blob --key "$work/test.pub" --bundle "$work/bundle.json" --insecure-ignore-tlog "$work/tampered"; then
  echo 'FAIL altered artifact accepted' >&2
  exit 1
fi
echo 'PASS original signature verified and modified artifact rejected'
# This is an offline artifact exercise. It does not enforce image admission.
