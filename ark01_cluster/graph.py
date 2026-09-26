"""ARK-01 compositional character graph and weighted propagation."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import json

CHANNELS = ("LETTER", "NIKUD", "TAAMIM", "TAGIN")
HEBREW = list("אבגדהוזחטיכלמנסעפצקרשת")

class Status(str, Enum):
    SOURCED = "sourced"
    PROPOSED = "proposed"
    UNRESOLVED = "unresolved"

@dataclass
class Edge:
    target: str
    weight: float = 0.0
    status: Status = Status.UNRESOLVED
    source_id: Optional[str] = None
    locator: Optional[str] = None

@dataclass
class Node:
    node_id: str
    kind: str
    value: Optional[str] = None
    metadata: dict = field(default_factory=dict)

class ARK01Graph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Edge]] = {}
        self.root_registry = [
            {"root_slot": r, "name": None, "source_id": None, "locator": None,
             "evidence_status": "unresolved",
             "relations": [{"relation_slot": k, "target": None, "weight": 0.0,
                            "status": "unresolved", "source_id": None, "locator": None}
                           for k in range(1, 32)]}
            for r in range(1, 33)
        ]

    def add_node(self, node_id, kind, value=None, **metadata):
        self.nodes[node_id] = Node(node_id, kind, value, metadata)
        self.edges.setdefault(node_id, [])

    def add_edge(self, source, target, weight, status=Status.UNRESOLVED,
                 source_id=None, locator=None):
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("Both edge endpoints must exist")
        if not -1.0 <= weight <= 1.0:
            raise ValueError("weight must be in [-1, 1]")
        self.edges[source].append(Edge(target, weight, Status(status), source_id, locator))

    def build_scaffold(self):
        # 231 canonical unordered pairs plus 90 explicitly unassigned extensions.
        gates = []
        for i, a in enumerate(HEBREW):
            for b in HEBREW[i+1:]:
                gates.append((f"G{len(gates)+1:03}", a, b, "canonical_pair"))
        while len(gates) < 321:
            gates.append((f"G{len(gates)+1:03}", None, None, "extension_unassigned"))
        for gid, a, b, gate_status in gates:
            self.add_node(gid, "gate", metadata={"status": gate_status})
            for side, letter in (("A", a), ("B", b)):
                if letter is None:
                    continue
                endpoint = f"{gid}:{side}:{letter}"
                self.add_node(endpoint, "letter_endpoint", letter, gate=gid, side=side)
                self.add_edge(gid, endpoint, 1.0, Status.SOURCED, "system:canonical-22-pair", "enumeration")
                for channel in CHANNELS:
                    cid = f"{endpoint}:{channel}"
                    self.add_node(cid, "character_channel", channel, letter=letter)
                    self.add_edge(endpoint, cid, 1.0, Status.PROPOSED, "architecture:channel-decomposition", channel)
                    for root in range(1, 33):
                        rid = f"{cid}:ROOT{root:02}"
                        self.add_node(rid, "root_instance", metadata={"root_slot": root, "name": None})
                        self.add_edge(cid, rid, 0.0, Status.UNRESOLVED, "registry:32-slots", str(root))
        return self

    def propagate(self, seeds: Dict[str, float], steps=1, include_proposed=False):
        values = {nid: 0.0 for nid in self.nodes}
        for nid, val in seeds.items():
            if nid not in self.nodes:
                raise KeyError(f"Unknown seed node: {nid}")
            values[nid] = float(val)
        allowed = {Status.SOURCED}
        if include_proposed:
            allowed.add(Status.PROPOSED)
        for _ in range(max(0, steps)):
            nxt = dict(values)
            for src, edges in self.edges.items():
                for edge in edges:
                    if edge.status in allowed:
                        nxt[edge.target] += values[src] * edge.weight
            values = nxt
        return values

    def counts(self):
        return {
            "gates": 321,
            "canonical_unordered_pairs": 231,
            "extension_slots": 90,
            "endpoint_instances": sum(n.kind == "letter_endpoint" for n in self.nodes.values()),
            "channel_nodes": sum(n.kind == "character_channel" for n in self.nodes.values()),
            "root_instances": sum(n.kind == "root_instance" for n in self.nodes.values()),
            "root_slots": 32,
            "relations_per_root": 31,
            "relations_per_channel": 32 * 31,
            "weighted_edges": sum(map(len, self.edges.values()))
        }

def export_registry(graph, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"schema_version":"0.1.0","root_slots":graph.root_registry},
                  f, ensure_ascii=False, indent=2)
