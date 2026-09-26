# ARK-01 Query-Conditioned Symbolic Propagation

This module implements a source-governed symbolic execution skeleton, not a weighted graph or statistical model.

## Execution contract
A query is compiled by the caller into a QueryPlan: logical cut, needed depth, relevant letter symbols, roots, names, and selected logic slots. Letter internals are recursive/open-ended Fragment trees. Depth is query-specific; there are no fixed channels.

Propagation composes fragments → letter/root parts → roots → letters/names → selected logic-name entries. A rule can fire only when its provenance is explicitly verified and its logic-name identifier is selected by the query plan. Missing source records remain unresolved; the engine never fabricates the 175 logic names, roots, or rules.

The current 175-slot registry is a set of identifiers only. Populate it from the source corpus with exact source locators before treating entries as authoritative. This is a deterministic symbolic execution scaffold; it does not yet claim trillions of operations or a complete ARK answer system.
