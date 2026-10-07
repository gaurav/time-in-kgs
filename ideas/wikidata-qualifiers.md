# Wikidata qualifiers as a worked example of "what was true when"

## What it is

Wikidata attaches **qualifiers** to statements (<https://www.wikidata.org/wiki/Help:Qualifiers>)
and gives each statement a **rank** (<https://www.wikidata.org/wiki/Help:Ranking>: preferred,
normal, deprecated). The time-related qualifiers are:

- `P580` start time and `P582` end time, for facts that hold over an interval;
- `P585` point in time, for facts that hold at an instant (a census count);
- `P459` determination method, `P1480` sourcing circumstances, and references, for evidence.

Raleigh, North Carolina (<https://www.wikidata.org/wiki/Q41087>) illustrates it. Its population
(`P1082`) has several statements, each with a `P585` date and a `P459` method (census vs
estimate), and the 2020 census value is ranked *preferred*. Its head of government (`P6`) has
one statement per mayor with `P580` start times, the current mayor ranked *preferred*. A query
for "the" population or "the" mayor returns the preferred statement; a query for the value at
a date filters on the qualifiers.

Formally, every Wikidata statement is a node (in RDF, a `wds:` statement entity) with the main
value plus qualifier and reference triples hanging off it. This is the same shape as a Biolink
association node and, with different plumbing, as an RDF-star quoted triple.

## Why it is relevant to time in KGs

- It is the **largest deployed KG that routinely records validity intervals on ordinary
  facts**, with over a decade of editing experience about what works. Judges will know it.
- It separates **three things the challenge text runs together**: when a fact holds (`P580`,
  `P582`, `P585`), how good the evidence is (`P459`, references), and which of several
  competing statements is currently endorsed (rank). The challenge's "distinguish what is true
  now from what was once true" and "evidence evolution" map onto these separately.
- It shows the **cost of doing time this way**: ranks are set by hand, there is no inference
  (nothing flags a mayor whose term overlaps the previous one), and every consumer has to
  remember to filter by qualifier. That is a clear statement of what a reasoning layer has to
  add.

## Which judging criteria it serves

- **Temporal Modeling Innovation (25%)**: as a baseline and a vocabulary for discussing
  alternatives. The innovation would be in what we add (axioms, inference), not in the pattern
  itself.
- **Feasibility & Integration (15%)**: statement-level qualifiers are exactly how Biolink and
  TRAPI carry edge properties, so the pattern integrates with ROBOKOP-style graphs without
  changing their shape.

## Gaps and risks against the rubric

- **Not biomedical.** Wikidata does hold drugs, diseases, and trials, but its temporal
  qualifiers are densest on political and demographic facts. It is a reference pattern, not a
  data source for this challenge.
- **No reasoning.** Nothing in Wikidata enforces that `P582` is after `P580`, or that two
  preferred statements are not simultaneously valid. Under Reasoning Correctness (25%) and
  Ontology Rigor (20%) the pattern scores nothing on its own; its role is to make the gap
  concrete.
- **Qualifiers are untyped time.** There is no distinction between the time a fact holds
  (valid time) and the time it was recorded (transaction time), which the challenge's
  "no temporal leakage" criterion depends on. Wikidata's edit history is the transaction time,
  but it is outside the statement model.

## Smallest useful experiment

Take one biomedical fact whose truth changed, for example a guideline recommendation that was
revised, or a drug label that gained a boxed warning, and represent it three ways:

1. **Wikidata-style**: a statement node with `P580`/`P582`-like qualifiers and a rank.
2. **RDF-star**: the triple quoted, with validity-interval and provenance properties on it.
3. **Biolink + OWL-Time + PROV-O**: an association with `temporal_interval_qualifier` pointing
   at a `time:ProperInterval`, and `prov:generatedAtTime` / `prov:invalidatedAtTime` for when it
   became and stopped being the endorsed claim.

Then write the same three questions against each ("what is recommended now?", "what was
recommended on date D?", "when did the recommendation change and on what evidence?") and
tabulate what each representation can answer by lookup, what needs inference, and what cannot
be asked at all. That table is a page of the Phase 1 write-up.

## Open questions

- Which of Wikidata's qualifier semantics does the Biolink `temporal_interval_qualifier` slot
  intend to cover, and does Biolink have an analogue of rank (it has `knowledge_level` and
  `agent_type`, which are about evidence rather than endorsement)?
- Is valid time versus transaction time (bitemporal modeling, as in SQL:2011) the right frame
  for "no temporal leakage", and has anyone applied it to a biomedical KG?
