# Competency questions: pharmacovigilance (`PV`)

Domain named by NIH as "pharmacovigilance". Temporal relationships between exposure and event
are the core of causality assessment here (the temporality criterion, dechallenge and
rechallenge, time to onset), and safety evidence changes as reports accumulate and labels are
revised.

Public data candidates are in [resources/README.md](../resources/README.md): FDA FAERS
(reports with event dates and drug start and end dates), DailyMed and openFDA (label versions),
ClinicalTrials.gov (trial records with version history). Patient-level questions use synthetic
patients. Field definitions and the ID scheme are in [README.md](README.md).

## Easy

### CQ-PV-E01: When did the label for drug D first carry warning W, and what was the latest label version in force on date T?

- **Why it is temporal**: label versions have validity intervals; a warning has a first-appearance
  date.
- **Minimal data**: label versions with effective dates and the warnings each contains.
- **Expected answer**: a date and the version identifier valid at T.
- **Criterion**: Feasibility & Integration (15%): DailyMed and openFDA already expose this;
  the graph must preserve it.
- **A static KG gets this wrong because**: "D has warning W" has no start, so the warning
  appears to have always existed.

### CQ-PV-E02: Which drugs was synthetic patient P exposed to on date T, and at what dose?

- **Why it is temporal**: the pharmacovigilance form of CQ-CP-E01: exposure intervals
  containing an instant, with dose steps as sub-intervals.
- **Minimal data**: exposure intervals with dose per interval.
- **Expected answer**: a set of drug and dose pairs.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%).
- **A static KG gets this wrong because**: it returns every drug ever recorded for P.

### CQ-PV-E03: What were the approved indications of drug D on date T?

- **Why it is temporal**: indications are added and sometimes withdrawn; each is an interval.
- **Minimal data**: indication approvals and withdrawals with dates.
- **Expected answer**: the set valid at T.
- **Criterion**: Feasibility & Integration (15%).
- **A static KG gets this wrong because**: the indication set is the union over all time, so
  off-label use at T is misclassified as on-label.

## Medium

### CQ-PV-M01: For adverse-event report R, which drugs were co-administered during the 30 days before the event onset, and which were started within 7 days of it?

- **Why it is temporal**: interval overlap with a fixed-length lookback window, and a
  proximity test on start dates.
- **Minimal data**: event onset date; drug intervals from the report (FAERS has start and end
  dates per drug, often missing or partial).
- **Expected answer**: two drug sets, and an explicit list of drugs whose dates were too
  incomplete to classify.
- **Criterion**: Feasibility & Integration (15%): real reports have partial dates
  (year-month only), so the integration has to represent imprecise instants.
- **A static KG gets this wrong because**: every drug on the report is "co-administered".

### CQ-PV-M02: Was adverse event A for drug D reported before or after the label change that added warning W, and does the answer change when "reported" means the event date rather than the report receipt date?

- **Why it is temporal**: two instants for the same report (valid time and transaction time)
  compared against a label version boundary. The counts of events before a label change are a
  standard signal-evaluation input.
- **Minimal data**: report with event date and receipt date; label version dates.
- **Expected answer**: a classification under each definition, and the reports whose
  classification differs.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%).
- **A static KG gets this wrong because**: it cannot order reports against the label change
  at all.

### CQ-PV-M03: For synthetic patient P on drug D, is there a positive dechallenge and rechallenge: did event A resolve after D was stopped and recur after D was restarted?

- **Why it is temporal**: a sequence pattern over two kinds of interval (exposure and event):
  exposure, event onset during exposure, exposure end, event end after exposure end, exposure
  restart, second event onset during the second exposure.
- **Minimal data**: P's exposure intervals for D (at least two) and event intervals for A.
- **Expected answer**: a boolean per pattern (dechallenge, rechallenge) with the matched
  intervals and the Allen relations between them.
- **Criterion**: Temporal Modeling Innovation (25%): the pattern is a small temporal grammar
  that the representation must make expressible. Secondary Workflow Relevance (15%): this is a
  Naranjo-style causality assessment input.
- **A static KG gets this wrong because**: "P took D" and "P had A" carry no sequence, so the
  single most informative pharmacovigilance pattern is invisible.

### CQ-PV-M04: Across a set of reports for drug D and event A, in which does the exposure precede the event, in which does the event precede the exposure, and does the ontology treat the second kind as evidence against causality rather than for it?

- **Why it is temporal**: the Bradford Hill temporality criterion. Event-before-exposure cases
  are either data errors or reverse causation (the event prompted the prescription), and a
  model that counts them as supporting evidence is wrong.
- **Minimal data**: per report, exposure start and event onset.
- **Expected answer**: counts in each class and the unclassifiable remainder; and an axiom or
  rule in the ontology under which a "caused by" association is inconsistent with an event
  onset before exposure start.
- **Criterion**: Ontology Rigor & Interoperability (20%): temporality as a machine-checkable
  constraint on a causal association, in Biolink and OAE terms.
- **A static KG gets this wrong because**: both classes are "D associated with A".

## Hard

### CQ-PV-H01: Which safety signals for drug D were supported by the evidence available at time T but have since been refined, contradicted, or withdrawn, and what is the status of each claim now?

- **Why it is temporal**: evidence evolution. A signal is a claim with a trajectory: raised by
  spontaneous reports, tested in a cohort study, attributed to confounding by indication, or
  confirmed and added to the label.
- **Minimal data**: claims about D and A with evidence items (reports, studies, regulatory
  actions) that have dates and a relation to the claim (supports, refines, contradicts,
  withdraws); a status rule.
- **Expected answer**: for each claim, its status at T and now, with the evidence events
  between.
- **Criterion**: Clinical or Public-Health Workflow Relevance & Impact (15%): a regulator or
  formulary committee asks exactly this. Secondary Temporal Modeling (25%).
- **A static KG gets this wrong because**: the challenge text's "treat contradictory
  scientific claims as equally valid".

### CQ-PV-H02: Using only reports received on or before date T, what is the disproportionality signal for drug D and event A, how does it evolve as T advances, and how does the trajectory relate to the dates of regulatory action?

- **Why it is temporal**: no-leakage computation over a growing report set. The signal at T
  must use only reports with receipt date at or before T; using event dates instead would leak
  reports not yet received.
- **Minimal data**: all reports with receipt dates, drug and event codes; regulatory action
  dates.
- **Expected answer**: a time series of the signal statistic (for example, proportional
  reporting ratio with a confidence interval) indexed by T, with the regulatory actions
  marked, and a statement of which reports were excluded at each T and why.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%).
- **A static KG gets this wrong because**: it computes one signal over all reports, which
  answers "is there a signal now?" and nothing about when it became detectable.

### CQ-PV-H03: For a patient treated with drug A and then switched to drug B, with an adverse event shortly after the switch, which exposure window or windows are consistent with the event given each drug's known time-to-onset distribution and A's elimination half-life?

- **Why it is temporal**: durations and uncertainty combined with sequence. An event two days
  after a switch may be more plausibly attributable to A's washout than to B, depending on
  latency distributions that are themselves evidence with dates and sources.
- **Minimal data**: exposure intervals for A and B; event onset; per-drug time-to-onset
  distributions and half-lives with their sources.
- **Expected answer**: a ranked attribution with the windows and parameters used, and an
  explicit "indeterminate" where the distributions overlap.
- **Criterion**: Clinical or Public-Health Workflow Relevance & Impact (15%): this changes
  which drug a clinician stops or reports. Secondary Temporal Modeling (25%) for durations and
  uncertainty.
- **A static KG gets this wrong because**: both drugs are "associated with" the event, with no
  way to use the sequence or the latencies.
