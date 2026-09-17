# Call Flows

## M1 target call flow

The initial ACD number is represented as `7000`; agents are `1001` and `1002`. These identifiers are lab defaults and will later move to environment/configuration data.

```mermaid
sequenceDiagram
    participant C as Caller UA
    participant K as Kamailio
    participant F as FreeSWITCH
    participant A as Agent UA

    C->>K: INVITE sip:7000@lab
    K->>F: INVITE sip:7000@freeswitch
    F-->>K: 100 Trying
    F-->>K: 180/183
    K-->>C: provisional response
    Note over F: Caller enters ACD/queue logic
    F->>K: INVITE sip:1001@lab
    K->>A: INVITE
    A-->>K: 180 Ringing
    K-->>F: 180 Ringing
    A-->>K: 200 OK + SDP
    K-->>F: 200 OK + SDP
    F->>K: ACK
    K->>A: ACK
    F-->>K: 200 OK + SDP (caller leg)
    K-->>C: 200 OK + SDP
    C->>K: ACK
    K->>F: ACK
    Note over C,A: RTP is anchored/handled by FreeSWITCH, not Kamailio
```

## What to inspect

For every milestone we will capture:

- Call-ID and dialog identifiers.
- Via, Record-Route and Contact behavior.
- SDP offer/answer addresses and codecs.
- INVITE retransmissions and response timing.
- Which component generates each call leg.
- RTP source/destination addresses and negotiated payload types.
- BYE direction and teardown behavior.

The goal is to correlate the logical ACD behavior with the actual wire protocol rather than treating SIP as a black box.
