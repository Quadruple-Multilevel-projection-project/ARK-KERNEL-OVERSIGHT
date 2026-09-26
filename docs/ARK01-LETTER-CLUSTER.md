# ARK-01 Letter Cluster Scaffold

A compositional graph model: each letter endpoint contains LETTER, NIKUD, TAAMIM, TAGIN channel nodes. Each channel references 32 root slots; each root slot reserves 31 relation slots (992 per channel). Source-derived names and relation targets remain null until extracted with citations.

## Gate plan
- G001-G231: canonical unordered pairs from the 22 Hebrew letters.
- G232-G321: reserved extension gates, deliberately unassigned pending source evidence.

## Weighted propagation
Edges carry weights in [-1,1], provenance, and status. Propagation includes sourced edges by default; proposed edges require explicit opt-in; unresolved edges never propagate.

## Engineering note
This is a symbolic graph computation model, not a claim of biological neural or quantum behavior. Root/relation slots are placeholders, not extracted linguistic claims.
