#!/usr/bin/env python3
"""Offline cross-file checks; do not certify SIP routing or RTP."""
import ipaddress
import re
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]

def validate(public_ip="127.0.0.1"):
    ipaddress.IPv4Address(public_ip)
    cfg = (ROOT / "kamailio/kamailio.cfg").read_text()
    xml = (ROOT / "freeswitch/conf/freeswitch.xml").read_text()
    tree = ET.fromstring(xml.replace("__LAB_PUBLIC_IP__", public_ip))
    configs = {c.attrib["name"]: c for c in tree.findall("./section/configuration")}
    modules = {m.attrib["module"] for m in configs["modules.conf"].findall("./modules/load")}
    assert {"mod_sofia", "mod_callcenter", "mod_dialplan_xml", "mod_dptools", "mod_event_socket"} <= modules, "Missing required FS module"
    sofia = {p.attrib["name"]: p.attrib["value"] for p in configs["sofia.conf"].findall("./profiles/profile/settings/param")}
    assert sofia["ext-rtp-ip"] == public_ip
    assert sofia["rtp-ip"] == "172.28.0.20"
    cc = configs["callcenter.conf"]
    queues = {q.attrib["name"] for q in cc.findall("./queues/queue")}
    agents = {a.attrib["name"]: a for a in cc.findall("./agents/agent")}
    assert set(agents) == {"1001", "1002"}
    for name, agent in agents.items():
        assert agent.attrib["contact"].endswith(f"{name}@172.28.0.10:5062"), "Agent leg must use internal edge socket"
    for tier in cc.findall("./tiers/tier"):
        assert tier.attrib["agent"] in agents and tier.attrib["queue"] in queues
    for action in tree.findall("./section/context/extension/condition/action"):
        if action.attrib["application"] == "callcenter":
            assert action.attrib["data"] in queues
    destinations = {c.attrib["expression"] for c in tree.findall("./section/context/extension/condition")}
    assert {"^7000$", "^9196$"} <= destinations
    assert 'modparam("usrloc", "use_domain", 0)' in cfg
    assert 'listen=udp:172.28.0.10:5062' in cfg
    assert cfg.count('__LAB_PUBLIC_IP__') == 3
    compose = (ROOT / "docker-compose.yml").read_text()
    bindings = re.findall(r'^\s+- "([^"]+)"$', compose, re.M)
    assert len(bindings) == 3 and all(b.startswith("127.0.0.1:") for b in bindings), "Loopback port bindings required"
    assert "8021:" not in compose and "5062:" not in compose
    return tree

if __name__ == "__main__":
    validate()
    print("PASS: XML, module/dialplan/queue references, edge sockets, and loopback bindings")
    print("Runtime SIP, endpoint reachability, and two-way audio remain unverified.")
