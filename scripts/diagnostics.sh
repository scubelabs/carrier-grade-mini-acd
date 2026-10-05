#!/usr/bin/env bash
# No .env or build credentials collected; SIP logs can contain identities/IPs.
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
out="evidence/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$out"
failed=0
capture() {
  local name=$1; shift
  if ! "$@" > "$out/$name.txt" 2>&1; then
    echo "Incomplete: $name (see evidence file)" >&2
    failed=1
  fi
}
capture commit git rev-parse HEAD
capture working-tree git status --short
capture versions docker version
capture services docker compose ps -a
capture logs docker compose logs --no-color --tail=400 kamailio freeswitch
capture registrations docker compose exec -T kamailio kamcmd ul.dump
capture sip-profile docker compose exec -T freeswitch fs_cli -x 'sofia status profile internal'
capture queues docker compose exec -T freeswitch fs_cli -x 'callcenter_config queue list'
capture agents docker compose exec -T freeswitch fs_cli -x 'callcenter_config agent list'
capture tiers docker compose exec -T freeswitch fs_cli -x 'callcenter_config tier list'
capture channels docker compose exec -T freeswitch fs_cli -x 'show channels'
echo "Evidence saved to $out (ignored by git). Review SIP identities/IPs before sharing."
exit "$failed"
