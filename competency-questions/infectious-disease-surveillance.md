# Competency questions: infectious-disease surveillance (`ID`)

Domain named by NIH as "infectious-disease surveillance". The challenge text mentions "exposure
windows in contact tracing" and "waves of outbreaks, variants, and available interventions".

No data has been chosen yet. Public candidates are noted in
[resources/README.md](../resources/README.md): Nextstrain and outbreak.info for dated variant
frequencies, CDC open data for case counts and intervention timelines. Contact-tracing data
would have to be synthetic. Field definitions and the ID scheme are in [README.md](README.md).

## Easy

### CQ-ID-E01: Which variant of pathogen P was dominant in region R during ISO week W?

- **Why it is temporal**: a point-in-time lookup over a frequency series; "dominant" is a
  property of a (region, week) pair, not of the variant.
- **Minimal data**: variant frequency estimates per region per week, each with the interval it
  describes.
- **Expected answer**: one variant (or a tie with frequencies), with the estimate's date and
  source.
- **Criterion**: Feasibility & Integration (15%): this is standard surveillance output; the
  graph must ingest it with its intervals intact.
- **A static KG gets this wrong because**: "variant V is dominant in R" is either asserted or
  not; several variants end up simultaneously dominant.

### CQ-ID-E02: From what date was intervention I (a vaccine, antiviral, or non-pharmaceutical measure) authorized or recommended in jurisdiction J, and for which population?

- **Why it is temporal**: a validity interval with a start, often with an eligibility scope
  that itself changes in steps (age groups added over time).
- **Minimal data**: authorization and recommendation events with dates, jurisdiction, and
  eligible population.
- **Expected answer**: a date (or list of dates with the population each one added) and the
  source.
- **Criterion**: Feasibility & Integration (15%).
- **A static KG gets this wrong because**: "I is recommended for population X" has no start,
  so it appears to have always been available.

### CQ-ID-E03: What was the surveillance case definition for disease D in force on date T, and when did it change?

- **Why it is temporal**: versioned definitions. A count of "cases" is only interpretable
  against the definition valid when each case was classified.
- **Minimal data**: case-definition versions with validity intervals and the criteria text or
  structured criteria.
- **Expected answer**: the version valid at T and the list of change dates.
- **Criterion**: Temporal Modeling Innovation (25%): a definition is a class whose extension
  changes over time, which is a modeling decision the design must make explicitly.
- **A static KG gets this wrong because**: one definition exists, and case series spanning a
  definition change are silently inconsistent.

## Medium

### CQ-ID-M01: Which contacts of case C had an exposure within C's infectious window, given C's symptom-onset date and the infectious period for the variant circulating at that time?

- **Why it is temporal**: interval arithmetic where the parameters are themselves
  time-indexed. The infectious window is derived from onset plus variant-specific
  pre-symptomatic and symptomatic infectious periods; the variant is inferred from the time
  and place if not sequenced.
- **Minimal data**: C's onset date; contact events with dates or intervals; per-variant
  infectious-period estimates with their validity (the estimate in use on that date).
- **Expected answer**: the subset of contacts whose exposure interval overlaps the infectious
  window, with the window and the parameter version used.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%).
- **A static KG gets this wrong because**: "C had contact with X" has no date, so every
  contact is a candidate exposure; and a single infectious-period value applied to every
  variant and every era is wrong for some of them.

### CQ-ID-M02: Was intervention I available to person P at the time of exposure E, given P's jurisdiction and eligibility on that date?

- **Why it is temporal**: an as-of check joining a person's attributes, an exposure instant,
  and the eligibility intervals from CQ-ID-E02.
- **Minimal data**: exposure date; P's age, jurisdiction, and risk-group memberships with
  their own validity; intervention eligibility intervals.
- **Expected answer**: a boolean with the eligibility rule and interval that decided it.
- **Criterion**: Clinical or Public-Health Workflow Relevance & Impact (15%): this is the
  question behind "preventable exposure" analyses that change outreach and allocation
  decisions.
- **A static KG gets this wrong because**: if I is ever available to P's group, the exposure
  is counted as preventable, including exposures before I existed.

### CQ-ID-M03: Which of two overlapping outbreak waves does case C belong to, given its onset date, and how is a case in the overlap handled?

- **Why it is temporal**: waves are intervals that can overlap; membership is an Allen
  `during` relation, and the overlap is where the model's handling of ambiguity shows.
- **Minimal data**: wave intervals per region (with the method that defined them); case onset
  dates.
- **Expected answer**: a wave assignment, or an explicit "ambiguous" with both candidates and
  any disambiguating evidence (sequenced variant).
- **Criterion**: Temporal Modeling Innovation (25%).
- **A static KG gets this wrong because**: waves without intervals cannot contain cases.

### CQ-ID-M04: Among a set of cases with known onset dates, which pairs could not have been infector and infectee given the serial-interval bounds for the variant, and what partial order remains?

- **Why it is temporal**: a partial order derived from instants and a duration range. If the
  gap between two onsets is outside the serial-interval bounds, that direction of transmission
  is excluded.
- **Minimal data**: onset dates; serial-interval minimum and maximum for the relevant variant
  and era.
- **Expected answer**: a set of excluded ordered pairs and the remaining directed acyclic
  graph of possible transmissions.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%).
- **A static KG gets this wrong because**: any case can have infected any other.

## Hard

### CQ-ID-H01: Which hypothesized transmission chains are temporally impossible, given onset dates, the incubation-period distribution of the variant circulating at each link, and the earliest detection date of each variant in the region, and does the ontology make such chains unsatisfiable?

- **Why it is temporal**: composition of constraints along a path (each link must respect the
  serial interval), plus a validity constraint on the variant (a chain cannot involve a
  variant before it was first detected in the region). "Temporally impossible inference
  paths" is the challenge text's phrase.
- **Minimal data**: a candidate chain (ordered cases with variant labels); onset dates;
  per-variant serial-interval bounds and first-detection dates.
- **Expected answer**: for each chain, "possible" or the first link that fails and why; for the
  ontology, a reasoner or rule-engine report showing the failing chain is inconsistent with
  the axioms rather than merely filtered by a query.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%); secondary Ontology Rigor
  (20%).
- **A static KG gets this wrong because**: chains are paths over undated edges; all are
  possible.

### CQ-ID-H02: Which risk estimates (severity, transmissibility, vaccine effectiveness) were current when public-health advisory A was issued, which have since been superseded, and which advisories still in force rest on superseded estimates?

- **Why it is temporal**: evidence evolution across two kinds of object. Estimates have
  validity intervals and supersession links; advisories have issue dates and their own
  validity; the question joins them.
- **Minimal data**: estimates with dates, sources, and `wasRevisionOf` links; advisories with
  issue and withdrawal dates and the estimates they cite.
- **Expected answer**: for each advisory, the estimates current at issue, their current status,
  and a flag where an in-force advisory cites a superseded estimate.
- **Criterion**: Clinical or Public-Health Workflow Relevance & Impact (15%): this is the
  question a health department asks when deciding which guidance to review. Secondary
  Temporal Modeling (25%).
- **A static KG gets this wrong because**: it "merges outdated guidance with current
  recommendations", in the challenge text's words.

### CQ-ID-H03: As of date T, using only sequences and case reports received by T, what was the apparent growth of variant V, and how does it differ from the estimate using everything now known for the same period?

- **Why it is temporal**: bitemporal data. Each sequence has a collection date (valid time) and
  a submission date (transaction time); reporting lag means the view as of T is systematically
  incomplete. The gap between the two estimates is the leakage a static analysis commits.
- **Minimal data**: sequences or case reports with both collection and submission dates and
  variant labels.
- **Expected answer**: two growth estimates for the same calendar window (as-of T, and current)
  with the count of records that were not yet available at T.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%): the no-leakage criterion
  applied to the data layer rather than the inference layer.
- **A static KG gets this wrong because**: it has one timestamp per record at best, so the
  as-of view is impossible and every retrospective estimate uses future information.
