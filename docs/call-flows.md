# Call Flows

## M1 queue call — answer before agent delivery

Caller is 2000; agents are 1001/1002; queue pilot is 7000. The dialplan answers
the caller immediately, so the caller leg's 200 OK/ACK occurs **before** agent
answer. Each FreeSWITCH leg has its own Call-ID and dialog.

```mermaid
sequenceDiagram
    participant C as Caller 2000
    participant K as Kamailio
    participant F as FreeSWITCH
    participant A as Agent 1001 or 1002
    C->>K: INVITE 7000
    K->>F: INVITE via private socket 5062
    F-->>K: 200 OK with caller SDP
    K-->>C: 200 OK
    C->>K: ACK
    K->>F: ACK
    Note over C,F: Caller answered; queue tone over RTP
    F->>K: New INVITE for available agent
    K->>A: INVITE using registration
    A-->>K: 180 Ringing
    K-->>F: 180 Ringing
    A-->>K: 200 OK with agent SDP
    K-->>F: 200 OK
    F->>K: ACK
    K->>A: ACK
    Note over C,A: FreeSWITCH bridges both RTP legs
    C->>K: BYE on caller dialog
    K->>F: BYE
    F-->>K: 200 OK
    K-->>C: 200 OK
    F->>K: BYE on agent dialog
    K->>A: BYE
    A-->>K: 200 OK
    K-->>F: 200 OK
```

## Echo and direct extension calls

Dial **9196** through Kamailio to FreeSWITCH. `answer` followed by `echo` creates
one SIP dialog and one bidirectional RTP leg, isolating media before queueing.
Direct calls between registered users are proxied by Kamailio and have direct
endpoint media; they do not prove the FreeSWITCH queue/media path.

## What to inspect

- Separate Call-IDs, tags, and CSeq values for caller and agent legs.
- Host-facing edge socket 5060 and container-facing socket 5062.
- Double Record-Route entries: host UAs reach the advertised host address;
  FreeSWITCH reaches the private Docker address. ACK/BYE follow these routes.
- Registration Contact and the observed source saved as the received destination.
- Agent location lookup is username-only in this single-realm lab.
- SDP from both sides: negotiated PCMU/PCMA, reachable `c=` address, `m=audio` port.
- Bidirectional RTP on each FreeSWITCH leg. Kamailio remains outside the media path.
- Clean BYE/200 OK in both directions and no lingering FreeSWITCH channels.

Packet capture, not this intended ladder, is the evidence for the real run.
