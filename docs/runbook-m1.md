# M1 First-Call Runbook

## Checkpoint and scope

Implementation is present; the first successful end-to-end queue call is still
pending. This runbook takes the lab through E0 (workstation), E1 (services), then
E2 (echo and queue call). Record evidence at each gate. A green static check is
not a working-call claim.

The initial topology is **three SIP endpoints on the Docker host**, using UDP:
agent 1001, agent 1002, and caller 2000. Windows softphones plus Docker Desktop
with WSL integration are the intended next local test. No carrier, PSTN number,
WebRTC client, or external routing service is needed for M1.

## E0 — Workstation and package access

Requirements: Docker/Compose v2 with BuildKit, Python 3, and SIP softphone
instances that can use different local SIP ports. Enable Docker Desktop WSL
integration for Ubuntu before running these commands in WSL.

```bash
cd ~/projects/scubelabs/carrier-grade-mini-acd
git status --short
git rev-parse HEAD
docker --version
docker compose version
docker run --rm hello-world
cp .env.example .env
```

Keep `.env` at `LAB_PUBLIC_IP=127.0.0.1` for the first same-machine test. This
sets the host-facing Record-Route address and FreeSWITCH's external RTP address;
it does not change published port bindings or rewrite the softphone's SDP.

### FreeSWITCH package credential

The official Debian binary repository requires a SignalWire Personal Access
Token. The old anonymous package URL/key setup has been replaced. Obtain a
package-access token using the [official installation instructions](https://developer.signalwire.com/freeswitch/foundations/getting-started/).
Do not paste it into chat, a command argument, `.env`, or git.

Create the credential locally without echoing the token:

```bash
mkdir -p .secrets
chmod 700 .secrets
umask 077
read -r -s -p 'FreeSWITCH package token: ' fs_package_token
printf '\n'
printf 'machine freeswitch.signalwire.com login signalwire password %s\n' \
  "$fs_package_token" > .secrets/fs-auth.conf
unset fs_package_token
chmod 600 .secrets/fs-auth.conf
./scripts/preflight.sh
```

Compose passes this ignored file as a BuildKit secret. The credential is mounted
only during package installation and is not copied into the image. No real token
is needed for the offline Python checks. Without package access, stop at offline
validation; a source-build alternative is outside this change.

## E1 — Build and prove the services

```bash
docker compose build --no-cache
docker compose up -d --wait
docker compose ps
docker compose logs --tail=150 kamailio freeswitch
docker compose exec -T kamailio kamcmd core.uptime
docker compose exec -T freeswitch fs_cli -x 'sofia status'
docker compose exec -T freeswitch fs_cli -x 'show codecs'
docker compose exec -T freeswitch fs_cli -x 'callcenter_config queue list'
```

Expected: FreeSWITCH `internal` profile RUNNING on `172.28.0.20:5060`,
PCMU/PCMA codecs available, and queue `support@default` present. FreeSWITCH's
healthcheck gates Kamailio startup; it is not a complete call-quality check.
Confirm both processes remain up and no required module fails to load.

For a parser check against the exact image:

```bash
docker compose run --rm --no-deps kamailio \
  kamailio -c -f /etc/kamailio/kamailio.cfg
```

## E2a — Register caller and agents

| Setting | Agent 1 | Agent 2 | Caller |
|---|---|---|---|
| SIP user / authentication user | 1001 | 1002 | 2000 |
| Domain / server | 127.0.0.1 | 127.0.0.1 | 127.0.0.1 |
| Registrar / outbound proxy | 127.0.0.1:5060 | 127.0.0.1:5060 | 127.0.0.1:5060 |
| Transport | UDP | UDP | UDP |
| Suggested local SIP port | 5071 | 5072 | 5073 |
| Codec preference | PCMU, PCMA | PCMU, PCMA | PCMU, PCMA |
| Password | Unchecked in M1 | Unchecked in M1 | Unchecked in M1 |

If the softphone requires a password field, use a throwaway lab value; the proxy
does not challenge or validate it. The identity allowlist is not authentication.
Disable STUN/ICE/SRTP for this basic local RTP test. Keep each endpoint registered
and available. Do not bind the endpoint's receiving socket only to loopback if
Docker must reach it through the host gateway.

```bash
docker compose exec -T kamailio kamcmd ul.dump
docker compose logs --tail=60 kamailio
```

Expect three records under location, with users 1001, 1002, and 2000. Registration
lives in Kamailio, **not** in FreeSWITCH. `sofia ... reg` will not show these users.
Inspect Contact and received address/port. Kamailio stores the observed REGISTER
source so that a private/loopback Contact does not alone control delivery.

## E2b — Prove echo before queueing

From caller 2000, dial **9196** (`sip:9196@127.0.0.1:5060`). Speak and confirm
your voice returns; then hang up. Capture INVITE, 200 OK, ACK, SDP, RTP, and BYE.
If echo fails, fix reachability/SDP/codecs before changing queue behavior.

FreeSWITCH anchors this media. Its SDP `c=` address should match the reachable
`LAB_PUBLIC_IP`, and its `m=audio` port should be in **16384–16484**. The endpoint's
SDP must also advertise an IP/port reachable **from the FreeSWITCH container**.

### Windows / WSL / Docker audio gate

Loopback publishing and `LAB_PUBLIC_IP=127.0.0.1` do not prove that Docker
Desktop can send media back to a Windows endpoint. The endpoint may advertise
`127.0.0.1`, which means the container itself from FreeSWITCH's perspective.
Kamailio does not relay or rewrite RTP/SDP. Contact fixes address signaling only.

Inspect both SDP bodies and a packet capture. Configure the softphone to
advertise its reachable Windows adapter address and listen on that adapter, and
allow the required endpoint RTP ports through the host firewall. Verify the
return path. If containers still cannot reach the endpoint, use a deliberately
isolated, reachable topology and record its bindings/addressing; changing only
`LAB_PUBLIC_IP` cannot solve an unreachable endpoint. Keep the checked-in
loopback defaults until that topology has been verified. Separate-device/LAN
access requires an explicit isolated-network configuration and remains unproven.

## E2c — First queue call

Check agents and tiers:

```bash
docker compose exec -T freeswitch fs_cli -x 'callcenter_config agent list'
docker compose exec -T freeswitch fs_cli -x 'callcenter_config tier list'
docker compose exec -T freeswitch fs_cli -x 'callcenter_config agent set status 1001 Available'
docker compose exec -T freeswitch fs_cli -x 'callcenter_config agent set status 1002 Available'
```

Dial **7000** from caller 2000. Caller leg is answered **before** an agent picks
up, then gets queue tone. FreeSWITCH selects an available agent, originates a
separate agent leg through Kamailio's private port 5062, and bridges after answer.
Confirm speech in both directions, hang up from the caller, then repeat with
agent-side hangup.

Take agent 1001 out of selection to prove delivery to 1002:

```bash
docker compose exec -T freeswitch fs_cli -x 'callcenter_config agent set status 1001 Logged Out'
# Dial 7000, answer on 1002, verify audio and hangup.
docker compose exec -T freeswitch fs_cli -x 'callcenter_config agent set status 1001 Available'
```

Registration and ACD availability are separate state. An available but
unregistered agent produces a failed delivery attempt. After repeated missed
calls, explicitly restore availability before retesting. Queue/agent state may
persist in FreeSWITCH's container database across a process restart; check it
rather than assuming XML was re-applied.

## Diagnostics and failures

```bash
./scripts/diagnostics.sh
docker compose exec -T freeswitch fs_cli -x 'show channels'
```

Diagnostics are saved under ignored `evidence/`; they contain no build credential
but can contain SIP identities and network addresses. Review before sharing.
The collector returns nonzero if any collection command fails.

| Symptom | First check |
|---|---|
| Build fails with 401 | Package credential/access; do not expose the token |
| Kamailio does not start | FreeSWITCH health and proxy parser/log output |
| Registration fails | Host port 5060 conflict, correct proxy, UDP, Docker WSL integration |
| Agent leg gets 404 | `kamcmd ul.dump`; user must be registered, even if FS says Available |
| Caller hears queue tone, no agent rings | Agent status, tiers, outbound INVITE and registered received address |
| Call connects but audio missing | Both SDP addresses, endpoint RTP reachability, firewall, RTP ports |
| Call drops after about 30 seconds | Missing ACK, Contact/Record-Route and socket reachability |
| No queue call after missed attempts | Restore agent Available; inspect persisted status |
| Channels remain after hangup | Both SIP dialogs' BYE/200 OK; `show channels` |

## Definition of done

- [ ] Record Docker/WSL versions and repository commit.
- [ ] Both services remain healthy; required modules/codecs loaded.
- [ ] Caller and both agents registered in Kamailio.
- [ ] Echo has media in both directions and clean teardown.
- [ ] 7000 enters `support@default` and delivers to an available agent.
- [ ] Agent 1002 receives a call with 1001 logged out.
- [ ] Caller/agent hear each other, backed by both-direction RTP evidence.
- [ ] Caller-side and agent-side hangups leave no active channels.
- [ ] Captured SIP ladder matches the documented early-answer flow.

Stop the lab with `docker compose down`. Avoid `docker compose down -v` unless
you specifically intend to remove any volumes introduced in future milestones.
No production, HA, authentication, or real call proof is claimed by this PR.
