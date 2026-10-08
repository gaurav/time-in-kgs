# Competency questions: cross-cutting (`XX`)

Representation-level questions that any domain needs. Several map directly onto rubric
language: `XX-H01` onto "machine-verifiable axioms beyond the class hierarchy", `XX-H02` onto
"no temporal leakage", and `XX-H03` onto the six Phase 2 evaluation metrics.

Field definitions and the ID scheme are in [README.md](README.md).

## Easy

### CQ-XX-E01: Which assertions in the graph are valid at time T?

- **Why it is temporal**: the basic as-of view. Each assertion has a validity interval (valid
  time); the answer is the set whose interval contains T, plus assertions with no interval
  treated according to a stated policy.
- **Minimal data**: assertions with validity intervals; the policy for interval-less
  assertions.
- **Expected answer**: a subgraph, with the policy applied to interval-less assertions made
  explicit in the output.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%).
- **A static KG gets this wrong because**: every assertion is valid at every time.

### CQ-XX-E02: Which assertions have no validity interval, and which of those are of a type that should have one?

- **Why it is temporal**: a completeness check on the temporal annotation itself. Some facts
  are genuinely atemporal (a drug's molecular structure); others (a patient's medication) are
  not and an interval-less one is a modeling error or a data gap.
- **Minimal data**: assertions; an ontology that marks which association types are expected to
  carry intervals.
- **Expected answer**: counts and a list, split into "atemporal by design" and "missing
  interval". The second number is one input to the Phase 2 "attribute richness" metric.
- **Criterion**: Temporal Modeling Innovation (25%): the design must say which facts are
  time-indexed and why.
- **A static KG gets this wrong because**: the question is meaningless when nothing has an
  interval.

### CQ-XX-E03: For assertion S, when did it enter the graph, from which source, and does that differ from the time the fact is asserted to hold?

- **Why it is temporal**: valid time versus transaction time. A lab result holds on the day it
  was drawn (valid time) but enters the record when resulted (transaction time); a guideline
  holds from its effective date but was published earlier.
- **Minimal data**: per assertion, `prov:generatedAtTime` (or equivalent) and the source, plus
  the validity interval.
- **Expected answer**: both timestamps, the source, and the gap between them.
- **Criterion**: Feasibility & Integration (15%): PROV-O and Biolink's provenance slots
  already exist for this; the question is whether the design uses them.
- **A static KG gets this wrong because**: provenance without time cannot say when a fact
  became known, so leakage cannot even be defined.

## Medium

### CQ-XX-M01: Which pairs of assertions conflict only if time is ignored?

- **Why it is temporal**: mutually exclusive states (a chest tube present and removed; a drug
  active and discontinued; a case definition and its replacement) are consistent when their
  intervals are disjoint and inconsistent when they overlap.
- **Minimal data**: assertions with intervals; disjointness axioms between the state classes.
- **Expected answer**: pairs with their interval relation; those with overlapping intervals
  are genuine conflicts to investigate, the rest are the static graph's false conflicts.
- **Criterion**: Ontology Rigor & Interoperability (20%): the exclusivity must be stated as
  disjointness axioms the reasoner can use, not as application logic.
- **A static KG gets this wrong because**: every such pair is a contradiction, or, if the
  loader deduplicated, one state silently won.

### CQ-XX-M02: Given two events whose times are known only to intervals (for example, "about 6 weeks after" and "within 2 weeks of"), which Allen relations between them are possible, and which are ruled out?

- **Why it is temporal**: uncertainty in temporal position, which the rubric names explicitly.
  The answer is a disjunction of Allen relations, not one relation.
- **Minimal data**: bounds on each event's start and end; any known relation to a dated anchor.
- **Expected answer**: the set of possible relations (for example {before, meets}) with the
  constraint that produced each exclusion. This is interval-algebra constraint propagation.
- **Criterion**: Temporal Modeling Innovation (25%).
- **A static KG gets this wrong because**: it has no intervals; a naive date-stamped graph that
  collapses each event to a single date reports one relation with false confidence.

### CQ-XX-M03: What is the evidence timeline for assertion S: when was it first supported, when refined, when contradicted or retracted, and what is its current status?

- **Why it is temporal**: evidence evolution. The same claim can have several evidence items
  with their own dates and a status that changes as they accumulate.
- **Minimal data**: evidence items linked to the assertion with publication or report dates
  and a type (supports, refines, contradicts, retracts); a rule for deriving the current
  status.
- **Expected answer**: an ordered list of evidence events and a status per time segment, like
  a Wikidata rank that changes over time.
- **Criterion**: Temporal Modeling Innovation (25%): "evidence evolution" is in the criterion
  text.
- **A static KG gets this wrong because**: supporting and contradicting publications sit side
  by side with equal weight, which the challenge text calls out as a failure.

## Hard

### CQ-XX-H01: Does the ontology make temporally impossible configurations unsatisfiable, and can a standard reasoner show it?

- **Why it is temporal**: the configurations are (a) an effect whose interval precedes its
  cause, (b) a treatment that depends on a diagnosis but starts before the diagnosis's
  transaction time, (c) a fact whose valid time starts before the generation time of its only
  supporting evidence, and (d) an interval whose end precedes its start.
- **Minimal data**: an ontology with the relevant classes, OWL-Time and RO temporal relations,
  and axioms (disjointness, equivalence to restrictions, property characteristics, and where
  OWL DL is insufficient, rules in SWRL or SHACL) that exclude each configuration; a small
  instance graph with one deliberate violation of each kind.
- **Expected answer**: a reasoner report (ROBOT `reason`, whelk, HermiT, or SHACL validation)
  naming the unsatisfiable class or inconsistent individual for each violation, and a clean
  report for the uncorrupted graph. The write-up should state which configurations are caught
  by OWL alone and which need rules, since that distinction is itself a result.
- **Criterion**: Ontology Rigor & Interoperability (20%): this is the direct answer to
  "machine-verifiable axioms beyond the class hierarchy". Secondary Reasoning Correctness
  (25%).
- **A static KG gets this wrong because**: none of the four configurations is expressible, so
  none is forbidden.

### CQ-XX-H02: For an answer computed "as of" time T, can the system produce a derivation showing that every assertion used has transaction time at or before T?

- **Why it is temporal**: this is the operational definition of no temporal leakage. It is
  about the inference procedure, not just the data.
- **Minimal data**: assertions with transaction times; an inference engine that records the
  assertions each conclusion depends on.
- **Expected answer**: for each conclusion, the set of supporting assertions with their
  transaction times and the maximum of those times, which must be at or before T. A leak is a
  supporting assertion with a later transaction time; the system should surface it rather than
  silently use it.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%).
- **A static KG gets this wrong because**: it cannot distinguish an inference from facts known
  at T from one that used facts recorded later; in a predictive setting this is the classic
  leakage error.

### CQ-XX-H03: For a given dataset, what are the Phase 2 metrics for the temporal graph and for the static baseline built from the same source, and which differences are attributable to the temporal model?

- **Why it is temporal**: the comparison is the point. The rubric requires six metrics: logical
  inconsistencies or unsatisfiable classes, number of triples, relationship richness,
  attribute richness, class/property instantiation ratio, interlinking completeness.
- **Minimal data**: a documented procedure for producing the static baseline from the same
  input (for example, dropping all temporal annotations and collapsing intervals), both graphs,
  and the ontology.
- **Expected answer**: a table of the six metrics for both graphs with the computation method
  for each, and a short account of why each differs. Some will favour the static graph (fewer
  triples), which the write-up should say rather than hide.
- **Criterion**: Feasibility & Integration (15%) in Phase 1, where it shows the evaluation is
  planned; Evaluation Rigor (20%) in Phase 2.
- **A static KG gets this wrong because**: it is the baseline; the question is whether the
  temporal graph beats it on the metrics that matter and by how much.
