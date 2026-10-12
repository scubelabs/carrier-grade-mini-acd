# Learn the M1 implementation

## What and why

This lab gives you two different tools: Kamailio handles SIP messages and finds registered phones; FreeSWITCH answers calls and handles audio/queue treatment. Think of SIP as instructions arranging a conversation and RTP as the audio packets. Correct instructions alone do not prove you can hear the conversation.

Use the existing Medha first-voice-lab curriculum for the complete Windows/WSL, Docker and bare-metal journey. The source in this repository is authoritative for current behavior; Medha's bundled lab snapshot is pinned teaching material and may differ from a later implementation.

## Architecture and files

docker-compose.yml defines two containers on a private voice network. kamailio/kamailio.cfg handles REGISTER, initial INVITE and in-dialog routing. freeswitch/conf/freeswitch.xml defines media and dialplan treatment. Dockerfiles build dependencies; entrypoints render runtime addresses. scripts/preflight.sh and scripts/diagnostics.sh help observe configuration and services; scripts/validate-config.py and tests/test_config.py check configuration assumptions. Existing docs/architecture.md, docs/call-flows.md and docs/runbook-m1.md contain the architecture, call flow and run commands. Reuse them rather than creating duplicate uppercase documents.

## Code walkthrough at audited SHA 0ede99b

The following explains each statement in the REGISTER block of kamailio/kamailio.cfg. Use that pinned file when comparing code; later changes need a refreshed explanation.

| Statement | Meaning and reason |
|---|---|
| if (is_method("REGISTER")) | Select a registration message rather than treating it as a call |
| if (!($tU =~ "^(1001\u007c1002\u007c2000)$")) | Permit only the three lab identities in the To URI; this is an allowlist, not password authentication |
| sl_send_reply("403", "Unknown Lab User") | Reject an identity outside the lab set |
| exit | Stop processing after rejection |
| fix_nated_register() | Record received signaling address information for the registrar; does not repair audio addresses |
| if (!save("location")) sl_reply_error() | Save the phone's registration in location, or report the failure |
| xlog(...) | Record an operational registration observation; sanitize identities/addresses when sharing logs |
| exit | End REGISTER processing so it cannot enter INVITE routing |

Elsewhere, lookup("location") resolves a registered identity. t_relay() forwards signaling with transaction handling. record_route() keeps the proxy on subsequent dialog requests; loose_route() interprets that route for messages such as BYE. The echo/queue INVITEs are sent to FreeSWITCH; direct endpoint calls are a different media path. There is no external business API or durable multi-tenant registration database in this slice.

## Build, run and test

Follow docs/runbook-m1.md in order, including its prerequisites and package-access secret instructions. Do not place the package token in Git or logs. The build and operational commands are documented there; use the current commands rather than guessing from a walkthrough. For offline validation, run python3 scripts/validate-config.py and python3 -m unittest discover -s tests -v. Run the full Docker/service and call gates only on the authorized local lab. Static validation, registration, packet flow and audibility are distinct results.

Windows runs the endpoint while WSL provides the Linux development environment. Docker isolates process/filesystem dependencies and supplies a reproducible network. Bare-metal deployment installs those dependencies directly and requires explicit service, file permission, address and lifecycle management. It follows a separate Medha route; copying a Docker-private address to a physical server will not create that network.

## Practical exercise and troubleshooting

Predict the route, register a documented phone, inspect location, then place an echo call before testing the queue. Capture sanitized observations showing successful signaling, SDP destinations, two-way RTP, audible echo and cleanup after BYE. Then repeat the controlled queue test with both documented agents and hangup from each side. Save SHA, image versions, topology and commands. Do not call the exercise attempted until you supply your own evidence.

| Symptom | First evidence to inspect |
|---|---|
| No registration | Endpoint destination, published port, Kamailio logs and location dump |
| Registered but INVITE fails | Request URI, lookup, response code and FreeSWITCH readiness |
| Call answers but audio fails | Both SDP addresses, RTP port reachability and packet directions |
| Call ends but channels remain | BYE/ACK path, route headers and FreeSWITCH channel output |

Security: the unauthenticated lab is confined to its documented local scope. Reliability: registrations are memory-based and restarts lose them. Performance/scaling: no load or HA evidence exists; changing container count is not a capacity proof. Keep credentials, personal captures and production addressing out of commits.

## Knowledge check and mastery

Explain why REGISTER success does not prove RTP, why Contact repair does not rewrite SDP, and why an accepted BYE should be correlated with channel cleanup. Draw the echo route and the queue agent leg. Understanding is validated only after an assessed explanation, successful lab evidence and failure diagnosis. Current gates: implementation source available; walkthrough available in this PR; exercise not assessed; understanding unverified. Next learning: dialog/transaction state, SDP offer/answer, RTP addressing and NAT before authentication and HA.
