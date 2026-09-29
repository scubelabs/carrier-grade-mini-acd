# Carrier-Grade Mini ACD

> **SCubeLabs ecosystem** · [Platform](https://github.com/scubelabs/scubelabs) · [Architecture](https://github.com/scubelabs/ccaas-reference-architecture) · [Domain Model](https://github.com/scubelabs/ccaas-domain-model) · [Mini ACD](https://github.com/scubelabs/carrier-grade-mini-acd) · [SIP Lab](https://github.com/scubelabs/sip-troubleshooting-lab) · [VoxOne](https://github.com/scubelabs/voxone-showcase)

> **Role:** executable voice/ACD validation path · **Maturity:** M1 bootstrap · **Evidence:** implementation present; end-to-end registration, delivery and RTP verification pending

> A production-oriented lab for building an Automatic Call Distributor with Kamailio, FreeSWITCH, and modern distributed-systems patterns.

## Role in the SCubeLabs platform

This repository is the **executable vertical-slice laboratory** for the real-time voice spine. It turns architecture and domain contracts into observable SIP, media, queueing and agent-delivery behavior. It does not replace the authoritative platform domains; it is where integration assumptions are made runnable and testable.

**Upstream:** carrier/SIP endpoints, voice-edge policy and canonical platform contracts.  
**Owns in this lab:** local signaling path, media/call-control integration, queue experiment, test topology and evidence.  
**Downstream:** agent endpoint, observability, failure testing and later multi-carrier scenarios.

## Why this project exists

A basic queue demo is easy. A resilient voice platform is not. This project progressively builds an ACD while exposing the engineering decisions behind SIP signaling, RTP/media, call state, routing, failure handling, scaling, observability, and agent connectivity.

The objective is a **runnable engineering lab**, not a claim that the initial milestones are production-ready.

## Target architecture

```mermaid
flowchart LR
    C[Caller / SIP Test Endpoint] -->|SIP| K[Kamailio\nSIP Edge & Routing]
    K -->|SIP| F[FreeSWITCH\nMedia & Call Control]
    F --> R[ACD Routing Engine]
    R --> RS[(Redis\nEphemeral State)]
    R --> PG[(PostgreSQL\nDurable Data)]
    F --> A[Agent Endpoint\nSIP → WebRTC]
    K -. telemetry .-> O[Observability]
    F -. telemetry .-> O
    R -. telemetry .-> O
```

## Milestone 1 — Local SIP ACD

The first working milestone deliberately keeps the architecture small:

```text
Caller → Kamailio → FreeSWITCH → Queue → SIP Agent
```

Goals:

- Run the voice stack locally with Docker Compose. Ports bind to host loopback by default because SIP registration has no authentication in M1.
- Route SIP signaling through Kamailio.
- Send ACD traffic from Kamailio to FreeSWITCH.
- Register/test two SIP agent endpoints.
- Queue a caller and deliver the call to an available agent.
- Capture and explain the SIP ladder.
- Verify bidirectional RTP.
- Document failure behavior rather than hiding it.

## Roadmap

| Milestone | Capability |
|---|---|
| M1 | Local SIP ACD: Kamailio + FreeSWITCH + SIP agents |
| M2 | External routing engine and explicit agent/queue state |
| M3 | Redis-backed ephemeral state and PostgreSQL durable data |
| M4 | WebRTC agent endpoint |
| M5 | Metrics, logs, SIP tracing, Prometheus/Grafana |
| M6 | Failure injection, health-aware routing and recovery |
| M7 | Horizontal scaling and HA patterns |
| M8 | Multi-carrier ingress and routing policies |

## Repository layout

```text
.
├── docker-compose.yml
├── kamailio/
├── freeswitch/
├── routing-engine/
├── agent-ui/
├── database/
├── monitoring/
├── scripts/
├── tests/
└── docs/
```

Directories are introduced as the corresponding milestone becomes executable; we avoid empty architecture theater.

## Engineering questions

This lab is designed to make questions visible that toy ACD implementations often skip:

- Which component owns dialog, queue, and agent state?
- What happens to an established call if Kamailio fails?
- What happens when a FreeSWITCH node disappears before or during media handling?
- How are signaling and media scaled independently?
- How do we avoid stale agent state?
- How should retries work without causing duplicate call delivery?
- How do we trace one call across SIP, media, routing, and application events?
- Which state must survive a process, node, or region failure?

## Evidence and maturity

| Dimension | Current state |
|---|---|
| Architecture | Defined for the target lab path |
| Contracts | Evolving with the platform model |
| Implementation | M1 bootstrap committed |
| Integration evidence | Pending complete registration → queue → agent proof |
| Media evidence | Bidirectional RTP verification pending |
| Failure evidence | Planned for M6 |
| Load/HA evidence | Planned for M7+ |
| Production evidence | Not claimed |

## Security scope

The local lab starts on an isolated development network. Later milestones will explicitly address SIP authentication, topology hiding, TLS/SRTP, network policy, secret management, rate limiting, abuse controls, and production hardening.

**Do not expose the development configuration directly to the public Internet.**

## License

A license will be selected before the project is presented as reusable software. Until then, no license is granted merely by publication of the source.
