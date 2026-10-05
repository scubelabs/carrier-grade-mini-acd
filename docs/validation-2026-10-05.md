# M1 readiness review — 2026-10-05

Base: `aa09992` on main. This change prepares the lab for its first local call;
it does not mark M1 complete.

## Changes and reason

- Load Kamailio `siputils` for `has_totag()`; the previous config fails parser
  validation without it. Load `tmx` for transaction prechecks.
- Register only documented lab identities; use username-only location keys so
  FreeSWITCH agent legs resolve host registrations across differing SIP domains.
  This remains a single-realm, unauthenticated development lab.
- Save observed REGISTER destinations, use rport, and correct NAT Contacts for
  endpoint-originated signaling. This does not repair endpoint SDP or relay RTP.
- Separate public/private edge sockets and use double Record-Route so in-dialog
  traffic can traverse the host/container boundary without a private route
  becoming the host endpoint's only proxy address.
- Render advertised host address at startup; keep FreeSWITCH bind/SIP addresses
  on the internal Docker network and published ports on loopback.
- Replace the obsolete FreeSWITCH package repository/key setup with official
  authenticated Debian packages and BuildKit secret-based credentials.
- Install/load `mod_dialplan_xml`, required by the lab XML dialplan.
- Add 9196 echo, service health gating, offline checks, diagnostics, CI, and a
  staged runbook. Correct the SIP ladder to show answer before agent selection.

## Evidence obtained here

| Check | Result |
|---|---|
| XML parsing and cross-component references | Pass |
| Template rendering, argument preservation, invalid input rejection | 3 unittest cases pass, including multiple invalid address inputs |
| Bash/sh syntax | Pass |
| Git whitespace check | Pass |
| Native Kamailio 5.7.4 parser with rendered config | Pass; interface-resolution warnings in this restricted runtime |
| Exact pinned Kamailio 5.8.5 Docker parser | CI check added; result recorded separately in GitHub Actions |
| Native synthetic signaling experiment | Unable to start: runtime denies socket creation during TM initialization |
| Compose/image build and FreeSWITCH module startup | Not run here: Docker unavailable and package token not supplied |
| Real registration, echo, queue delivery, ACK/BYE, RTP/audio | Pending user's local workstation |

The locally extracted 5.7.4 binary was used only as a supplementary parser check;
the application image remains 5.8.5. No workaround to the runtime's socket
restriction was attempted. The synthetic experiment provides no call evidence.

## Remaining gates

1. Exact-image parser and Compose structure in CI.
2. Local package-access secret; full FreeSWITCH image build and module/codec proof.
3. Docker Desktop/WSL port reachability and all three registrations.
4. Echo with both SDP addresses reachable, then queue delivery to both agents.
5. Caller/agent hangup tests and packet evidence showing bidirectional RTP.

Package versions follow the official repository at build time; an image digest
and package-version lock should be recorded after the first successful build.
Windows endpoint receive paths, FreeSWITCH external SDP behavior, and double
Record-Route traversal are hypotheses to verify in that topology, not certified
outcomes. No change to production or to the user's WSL machine was made.

## References used in review

- [FreeSWITCH official package installation](https://developer.signalwire.com/freeswitch/foundations/getting-started/)
- [FreeSWITCH packaged module definitions](https://github.com/signalwire/freeswitch/blob/master/debian/control-modules)
- [Kamailio NAT helper 5.8](https://www.kamailio.org/docs/modules/5.8.x/modules/nathelper.html)
- [Kamailio Record-Route 5.8 source documentation](https://github.com/kamailio/kamailio/blob/5.8/src/modules/rr/doc/rr_admin.xml)
