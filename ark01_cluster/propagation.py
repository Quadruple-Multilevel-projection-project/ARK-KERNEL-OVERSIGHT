"""Query-conditioned symbolic propagation for ARK-01.

No numeric edge weights, matrices, statistical ranking, or fixed channel count.
All executable rules must be explicitly supplied and marked verified.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

@dataclass(frozen=True)
class Provenance:
    source_id: str
    locator: str
    verified: bool = False

@dataclass
class Fragment:
    """An open-ended internal string/substructure within a Hebrew letter."""
    fragment_id: str
    payload: str
    children: list["Fragment"] = field(default_factory=list)
    provenance: list[Provenance] = field(default_factory=list)

@dataclass
class Letter:
    symbol: str
    internal: list[Fragment] = field(default_factory=list)
    root_parts: list[str] = field(default_factory=list)

@dataclass
class Root:
    root_id: str
    parts: list[str]
    letters: list[str]
    provenance: list[Provenance] = field(default_factory=list)

@dataclass
class Name:
    name_id: str
    letters: list[str]
    root_ids: list[str] = field(default_factory=list)
    provenance: list[Provenance] = field(default_factory=list)

@dataclass(frozen=True)
class LogicRule:
    rule_id: str
    logic_name_id: str
    premise: str
    conclusion: str
    provenance: Provenance
    # The engine deliberately does not interpret unverified assertions as rules.

@dataclass
class QueryPlan:
    query: str
    logical_cut: str
    required_depth: int
    selected_logic_names: list[str] = field(default_factory=list)
    required_letters: list[str] = field(default_factory=list)
    required_roots: list[str] = field(default_factory=list)
    required_names: list[str] = field(default_factory=list)

@dataclass
class InferenceResult:
    answer_fragments: list[str]
    logic_names_used: list[str]
    trace: list[str]
    unresolved: list[str]

class LogicBook:
    """Registry for the 175 logic-name slots; names are never fabricated."""
    def __init__(self, entries: Optional[dict[str, str]] = None):
        self.entries = dict(entries or {})
        self.slots = [f"logic-{i:03d}" for i in range(1, 176)]

    def resolve(self, slot: str) -> Optional[str]:
        return self.entries.get(slot)

class PropagationEngine:
    def __init__(self, letters: dict[str, Letter], roots: dict[str, Root],
                 names: dict[str, Name], logic_book: LogicBook,
                 rules: Iterable[LogicRule] = ()):
        self.letters, self.roots, self.names = letters, roots, names
        self.logic_book = logic_book
        self.rules = list(rules)

    def _walk(self, fragment: Fragment, depth: int, trace: list[str]) -> list[str]:
        trace.append(f"fragment:{fragment.fragment_id}@depth={depth}")
        if depth <= 0 or not fragment.children:
            return [fragment.payload]
        out = []
        for child in fragment.children:
            out.extend(self._walk(child, depth - 1, trace))
        return out

    def propagate(self, plan: QueryPlan) -> InferenceResult:
        trace = [f"query:{plan.query}", f"logical-cut:{plan.logical_cut}",
                 f"requested-depth:{plan.required_depth}"]
        unresolved, facts = [], []
        for symbol in plan.required_letters:
            letter = self.letters.get(symbol)
            if letter is None:
                unresolved.append(f"letter:{symbol} absent from source registry")
                continue
            trace.append(f"letter:{symbol}")
            for fragment in letter.internal:
                facts.extend(self._walk(fragment, plan.required_depth, trace))
            for root_id in letter.root_parts:
                if root_id not in plan.required_roots:
                    plan.required_roots.append(root_id)
        for root_id in plan.required_roots:
            root = self.roots.get(root_id)
            if root is None:
                unresolved.append(f"root:{root_id} absent from source registry")
                continue
            trace.append(f"root-composition:{root_id}=>{','.join(root.letters)}")
            facts.extend(root.parts)
        for name_id in plan.required_names:
            name = self.names.get(name_id)
            if name is None:
                unresolved.append(f"name:{name_id} absent from source registry")
                continue
            trace.append(f"name-composition:{name_id}=>{''.join(name.letters)}")
            facts.append("".join(name.letters))
        used = []
        for slot in plan.selected_logic_names:
            resolved = self.logic_book.resolve(slot)
            if resolved is None:
                unresolved.append(f"{slot} has no source-verified registry entry")
            else:
                used.append(resolved)
        # Exact symbolic propagation: only source-verified rules may fire.
        known = set(facts)
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                if not rule.provenance.verified:
                    continue
                if rule.logic_name_id not in used:
                    continue
                if rule.premise in known and rule.conclusion not in known:
                    known.add(rule.conclusion)
                    trace.append(f"rule:{rule.rule_id}:{rule.premise}=>{rule.conclusion}")
                    changed = True
        if not known:
            unresolved.append("No answer derivable from the supplied source-backed structures.")
        return InferenceResult(sorted(known), used, trace, unresolved)
