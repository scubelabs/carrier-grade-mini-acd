#!/usr/bin/env bash
# Read-only: no containers started and no credential values displayed.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null || { echo 'FAIL: Docker/Compose v2 required; enable WSL integration.' >&2; exit 1; }
docker --version
docker compose version
docker info --format 'Engine {{.ServerVersion}} / {{.OSType}} / {{.Architecture}}'
[[ -s .secrets/fs-auth.conf ]] || { echo 'FAIL: missing .secrets/fs-auth.conf; see runbook.' >&2; exit 1; }
[[ -f .env ]] || echo 'NOTE: .env missing; LAB_PUBLIC_IP defaults to 127.0.0.1.'
docker compose config --quiet
python3 scripts/validate-config.py
if command -v ss >/dev/null; then
  echo 'Host listeners (check for conflicts on SIP 5060):'
  ss -lntu | awk 'NR==1 || /:5060([[:space:]]|$)/'
fi
echo 'Preflight passed. Image builds and runtime call validation are still required.'
