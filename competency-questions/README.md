# Competency questions

A **competency question** (CQ) is a question that an ontology or knowledge graph must be able
to answer for it to be fit for purpose (Grüninger and Fox, 1995; see
[resources/README.md](../resources/README.md)). Here they serve two jobs:

1. **Define success before building anything.** If a design cannot answer the hard questions
   below, it will not score under the challenge's Reasoning Correctness criterion no matter
   how elegant it is.
2. **Become the test suite.** Each CQ has a stable ID and an expected answer shape, so that in
   Phase 2 it can be turned into a query plus an assertion, run against both the temporal graph
   and a static baseline.

The challenge rubric is summarized in [AGENTS.md](../AGENTS.md). Every CQ names the Phase 1
criterion it mainly exercises so that coverage can be checked (matrix below).

## Files

| File | Domain code | Why this domain |
|---|---|---|
| [care-pathways.md](care-pathways.md) | `CP` | NIH's first named domain: "care pathways with sequential, non-interchangeable therapies". Anchored on a synthetic lung-cancer case with eleven dated visits |
| [infectious-disease-surveillance.md](infectious-disease-surveillance.md) | `ID` | NIH's second named domain. Exposure windows, variant waves, and time-varying parameters |
| [pharmacovigilance.md](pharmacovigilance.md) | `PV` | NIH's third named domain. Exposure-event timing, label changes, and evolving safety evidence |
| [cross-cutting.md](cross-cutting.md) | `XX` | Representation-level questions every domain needs, including the ones that map directly onto "machine-verifiable axioms" and "no temporal leakage" |

## ID scheme

`CQ-<domain>-<difficulty><nn>`, for example `CQ-CP-M03`. Difficulty is `E`, `M`, or `H`.
Numbers are two digits and never reused: if a question is dropped, mark it retired and keep the
ID in the file.

## Fields every CQ records

- **Question**: in plain language, with concrete values where the synthetic data allows.
- **Why it is temporal**: which temporal construct it depends on (instant, interval, ordering,
  duration, validity period, valid time vs transaction time, evidence evolution, uncertainty).
- **Minimal data**: the smallest set of facts and timestamps needed to answer it. This is what
  the prototype must ingest.
- **Expected answer**: the shape of a correct answer (a date, an interval, an ordered list, a
  boolean with a justification, a set of violations), and where known the actual answer from
  the synthetic case.
- **Criterion**: the Phase 1 criterion it mainly exercises, with weight, and any secondary one.
- **A static KG gets this wrong because**: what happens when the same facts are loaded without
  time. This is the seed of the Phase 2 head-to-head comparison.

## Difficulty rubric

- **Easy**: a lookup with a time filter. One entity, one point or interval, no inference. A
  graph that stores validity intervals answers these with a single query.
- **Medium**: ordering or interval algebra across several facts, "as-of" reconstruction of
  state at a date, or durations with uncertain bounds. Needs interval relations and usually a
  join across entity types.
- **Hard**: inference that must demonstrably avoid temporal leakage, reason over evidence that
  changed, combine intervals with causality or preconditions, or produce a reasoner-verified
  consistency result. These are the questions that separate a temporal KG from a static one
  with dates stuck on, and they are where the 25% Reasoning Correctness and 20% Ontology Rigor
  points are won or lost.

## Coverage matrix

Primary criterion per CQ. Secondary criteria are listed inside each question.

| Phase 1 criterion (weight) | CQs |
|---|---|
| Temporal Modeling Innovation (25%) | CP-M01, CP-M03, ID-E03, ID-M03, PV-M03, XX-E02, XX-M02, XX-M03 |
| Reasoning Correctness & Temporal Consistency (25%) | CP-E01, CP-M02, CP-H01, ID-M01, ID-M04, ID-H01, ID-H03, PV-E02, PV-M02, PV-H02, XX-E01, XX-H02 |
| Ontology Rigor & Interoperability (20%) | CP-M04, CP-H02, PV-M04, XX-M01, XX-H01 |
| Feasibility & Integration (15%) | CP-E02, CP-E03, ID-E01, ID-E02, PV-E01, PV-E03, PV-M01, XX-E03, XX-H03 |
| Clinical or Public-Health Workflow Relevance & Impact (15%) | CP-H03, ID-M02, ID-H02, PV-H01, PV-H03 |

Keep this table in sync when adding or retiring questions. Check for duplicate IDs with:

```sh
grep -rhoE 'CQ-[A-Z]{2}-[EMH][0-9]{2}' competency-questions/*.md | sort | uniq -d
```

## What is deliberately not here yet

- Queries. CQs are language-level until there is a schema to query against; adding SPARQL now
  would lock in a representation before the ideas have been compared.
- Guideline content. Several hard questions need versioned clinical guidelines or regulatory
  actions as data. Sources are noted per question; none has been ingested.
- Scoring. Phase 2 says effectiveness is measured on "shared benchmark tasks and test data"
  that NIH may provide. Until that is known, these CQs are our own benchmark, not NIH's.
