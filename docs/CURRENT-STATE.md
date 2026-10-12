# Verified current state — 12 October 2026

Audited default branch: 0ede99b515abdd805c472679d0d1cf8d0071e749. This is a local M1 lab, not a production ACD.

Implemented source: Docker Compose with loopback-published SIP and RTP ports; Kamailio location/registration and signaling routes; FreeSWITCH echo/queue XML configuration; health-gated startup; preflight, diagnostics, config validator and unittest files. The latest sampled GitHub M1 workflow succeeded. This documentation PR executes no new application tests and supplies no live call evidence.

Existing docs/validation-2026-10-05.md records parser/static checks and pending live gates. Its date/title do not imply every later change was tested locally. Live registration, queue delivery, both hangup directions, bidirectional RTP and audible audio require reproducible sanitized evidence pinned to the tested SHA. Conversational success reports should be captured with environment and observations before promoting maturity.

The lab accepts documented identities without SIP authentication; keep the documented local boundary. NAT Contact repair concerns signaling; it does not rewrite endpoint SDP or relay RTP. WSS/WebRTC is not implemented by this UDP/TCP setup, so VoxOne browser integration needs an explicit compatible edge.

Next milestone: record the controlled first-call proof using docs/runbook-m1.md; save actual command outputs, image/package versions, endpoint topology, both SDP destinations and hangup/channel cleanup. Link that evidence to the teaching exercise in docs/LEARNING.md. No deployment, HA, carrier-grade or learner-mastery claim is made.
