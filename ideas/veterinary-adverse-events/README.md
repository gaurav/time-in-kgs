# Veterinary adverse events and canine trial records as temporal test data

Two public, PHI-free sources with real timestamps, small enough to download by script and
query on a laptop, for the pharmacovigilance and care-pathway competency questions. This
directory holds the downloaders, a marimo notebook, and this note. Numbers below are from the
openFDA export dated 2026-10-06 and the ICDC fetch of 2026-10-08.

## What it is

- **openFDA Animal & Veterinary adverse events**
  (<https://open.fda.gov/apis/animalandveterinary/event/>): FDA Center for Veterinary Medicine
  reports, published quarterly as JSON under CC0. The six quarters 2025 Q1 to 2026 Q2 are
  about 22 MB zipped and hold 113,085 reports, 80,262 of them for dogs. Each report has the
  date FDA received it, the event onset date, per-drug first and last exposure dates,
  dechallenge and rechallenge flags, VeDDRA-coded reactions, ATCvet product codes, species,
  breed, age, weight, and outcome.
- **Integrated Canine Data Commons** (ICDC, <https://caninecommons.cancer.gov/>): NCI's data
  commons for canine cancer, 21 studies and 1,262 cases, open access with attribution, served
  by an open GraphQL API. The PRECINCT trials have dated visits and adverse events per dog;
  the osteosarcoma standard-of-care trials (COTC021, COTC022) have dated pathways (surgery,
  carboplatin doses, off-study date, survival) in study-level spreadsheets.
- **Scripts** (all `uv run`, dependencies declared in the file):
  - `download_openfda_animal.py --years 2025 2026` fetches the quarterly files to
    `data/openfda/animalandveterinary/event/` and records the export date.
  - `download_icdc.py` pages through the API into `data/icdc/<node>.json` and fetches the
    study-level files to `data/icdc/files/<study>/`, checking MD5s.
  - `analysis.py` is a marimo notebook: `uvx marimo edit --sandbox ideas/veterinary-adverse-events/analysis.py`
    (or `uvx marimo export html --sandbox ... -o out.html` for a static copy). It loads the
    JSON with DuckDB and works through the questions below.

## Why it is relevant to time in KGs

- Every report carries **two time axes**: when the event happened (onset, exposure dates) and
  when FDA learned of it (receive date). That is valid time versus transaction time, and it is
  exactly what the no-leakage requirement is about. The median lag from onset to receipt is
  6 days, but the 95th percentile is 245 days, so a signal computed on onset dates sees
  reports that did not exist yet.
- **Within-report ordering** is explicit: exposure intervals against onset, with flags for
  previous exposure, dechallenge (`ae_abated_after_stopping_drug`) and rechallenge
  (`ae_reappeared_after_resuming_drug`). That is the raw material for CQ-PV-M01, M03 and M04.
- The data has **real inconsistencies for axioms to catch**: 230 reports whose onset date is
  after the receive date (so the record was amended after receipt), and 17 drug rows whose
  last exposure precedes the first.
- ICDC gives a **per-dog pathway**: diagnosis, visits, adverse events with onset and
  resolution, off-study, the shape behind CQ-CP-E03, M03 and M04.

## Which judging criteria it serves

- **Reasoning Correctness & Temporal Consistency (25%)**: the notebook computes the
  proportional reporting ratio for isoxazoline flea-and-tick drugs against seizure terms
  month by month, once using only reports received by each month end and once by onset date.
  The honest series climbs from 1.36 to 1.80 over the 18 months as reports arrive; the leaky
  series starts at 1.90 in the first month, a signal nobody could have computed then. That
  is a concrete, reproducible demonstration of leakage and its absence.
- **Feasibility & Integration (15%)**: small, public, scriptable, licensed for reuse, and
  the openFDA human `drug/event` endpoint has an analogous schema, so a pipeline built here
  transfers to human FAERS.
- **Phase 2 Demonstrated Reasoning and Evaluation Rigor**: realistic data at a size where a
  static baseline (the same graph with temporal fields dropped) and the six required metrics
  can be computed in minutes.
- **Ontology Rigor (20%)**, partly: species map to NCBITaxon and breeds to the Vertebrate
  Breed Ontology, both OBO; ingredients to ChEBI or UNII; ICDC diseases to MONDO. The
  reaction and product codings do not (see gaps).

## Gaps and risks against the rubric

This is the part to read before anyone falls in love with the dataset.

- **The workflow is veterinary.** Human FAERS is equally public and equally free of PHI. The
  honest reasons to start here are size (22 MB for six quarters, against roughly 110 GB for
  openFDA's full human drug-event download) and ICDC as a matching care-pathway dataset.
  Judges score a *specific clinical or public-health workflow* (15%) and will think of human
  decisions. Either frame the entry as comparative oncology (the COTC trials exist to inform
  human trial design) or One Health, or use this data to build the pipeline and swap in human
  openFDA data for the write-up. The write-up must say which.
- **VeDDRA, ATCvet and VCOG-CTCAE are not OBO or NLM vocabularies.** They are the regulatory
  standards for this data, so keeping them is defensible, but the rubric rewards OBO/NLM
  reuse: add cross-references (HP or OAE for reactions, ChEBI for ingredients) for the terms a
  competency question touches.
- **openFDA is a current-view snapshot, not a history.** One record per report, no version
  history, no amendment date. An "as of T" answer can certify the set of reports received by
  T, not the content FDA held at T. Say so in any no-leakage claim.
- **ICDC's treatment nodes are empty through the API** (`agent_administration`,
  `follow_up`, `off_treatment`, `prior_therapy`, checked 2026-10-07). The dated pathways are
  in spreadsheets with study-specific columns, so each study needs its own mapping.
- **ICDC publishes dogs' names and owner-surname initials** (`case.patient_first_name`,
  `enrollment.initials`, both documented in the data model and shown in ICDC's own
  interface). The downloader fetches them because they are published fields; nothing here
  quotes them, and the notebook identifies cases by ICDC's public case IDs only.
- **The isoxazoline-seizure signal is known** (FDA's safety communication is dated
  2018-09-20), which makes it a validation target rather than a discovery. Showing the signal
  emerge *before* the communication needs the 2017 to 2019 quarters, which the downloader
  can fetch.

## Smallest useful experiment

The notebook is the first step and runs end to end. The next three, in order:

1. Fetch 2017 to 2019 and plot the as-of versus leaky PRR around 2018-09-20. If the honest
   series crosses a conventional threshold months before the communication, that is a slide.
2. Write a few hundred reports to Turtle as Biolink associations with OWL-Time intervals,
   plus two or three axioms (an exposure interval whose end precedes its start is
   unsatisfiable; an onset after receipt is a flagged class), and run
   [`tools/check-owl.scala`](../../tools/check-owl.scala) on the result.
3. Build the static baseline from the same reports by dropping the temporal triples and
   compute the six Phase 2 metrics for both graphs.

## Open questions

- Animal or human data for the Phase 1 write-up, given the workflow criterion?
- Which Biolink association class fits an adverse-event report, and how does the
  `temporal_interval_qualifier` problem (issue #2) apply to exposure intervals?
- Whether to ask ICDC when the treatment nodes will be populated, and whether their
  publication of dog names and owner initials is something they would want flagged.
