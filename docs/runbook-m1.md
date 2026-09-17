# M1 Runbook

## Status

M1 is a development bootstrap. The configuration is committed for review and iterative testing; it has **not yet been certified against every Docker/CPU/OS combination**. Pinning and compatibility fixes discovered during the first local run belong in the repository rather than being hidden.

## Prerequisites

- Docker Engine / Docker Desktop with Compose v2
- A SIP softphone for the caller and two agent instances (or equivalent SIP test tooling)
- Optional: Wireshark and/or sngrep

## Start the stack

```bash
git clone https://github.com/scubelabs/carrier-grade-mini-acd.git
cd carrier-grade-mini-acd
docker compose build --no-cache
docker compose up
```

In another terminal:

```bash
docker compose ps
docker compose logs -f kamailio freeswitch
```

## Agent registration

Configure two SIP endpoints against the Docker host IP / port `5060`:

| Agent | SIP user | Registrar/proxy |
|---|---|---|
| Agent 1 | `1001` | `<docker-host>:5060` |
| Agent 2 | `1002` | `<docker-host>:5060` |

M1 deliberately has **no SIP authentication**. Run it only on a trusted local development network. Authentication is added as a hardening milestone.

Confirm Kamailio logs show successful REGISTER processing.

## Place the first ACD call

From a third SIP endpoint, send an INVITE to:

```text
sip:7000@<docker-host>:5060
```

Expected logical path:

```text
Caller
  │ INVITE 7000
  ▼
Kamailio
  │ route to 172.28.0.20
  ▼
FreeSWITCH
  │ callcenter: support@default
  ▼
Agent selection
  │ outbound INVITE via Kamailio
  ▼
Agent 1001 or 1002
```

## Verification checklist

A successful M1 test must demonstrate all of the following before we call the milestone complete:

- [ ] Both agents REGISTER through Kamailio.
- [ ] Caller INVITE for 7000 reaches Kamailio.
- [ ] Kamailio forwards the ACD INVITE to FreeSWITCH.
- [ ] FreeSWITCH enters `support@default` call-center logic.
- [ ] FreeSWITCH originates an agent leg.
- [ ] Kamailio resolves the registered agent Contact.
- [ ] Agent receives the INVITE and answers.
- [ ] Caller receives 200 OK / ACK completes.
- [ ] Audio works in both directions.
- [ ] BYE tears down both legs cleanly.
- [ ] SIP capture matches the documented ladder.

## Useful diagnostics

```bash
# Kamailio logs
docker compose logs -f kamailio

# FreeSWITCH logs
docker compose logs -f freeswitch

# Container addressing
docker network inspect carrier-grade-mini-acd_voice
```

If FreeSWITCH is running, its CLI can be entered with the installed `fs_cli` binary inside the container:

```bash
docker exec -it scubelabs-freeswitch fs_cli
```

Useful commands include:

```text
sofia status
sofia status profile internal
callcenter_config queue list
callcenter_config agent list
callcenter_config tier list
show calls
```

## RTP caveat

Docker NAT and desktop virtualization can affect SDP/RTP addressing. The initial configuration advertises the lab container address for the FreeSWITCH media interface. If the SIP endpoints run on the host rather than inside the Docker network, the first test may expose an RTP reachability issue. That is intentional engineering work for M1: capture the SDP, identify the unreachable address, and then introduce an explicit advertised media address/NAT strategy instead of masking the problem.

## Definition of done

M1 is complete only when the call is proven end-to-end with signaling evidence and bidirectional media. A container that merely starts is not considered a successful milestone.
