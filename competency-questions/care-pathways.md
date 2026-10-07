# Competency questions: care pathways (`CP`)

Domain named by NIH as "care pathways with sequential, non-interchangeable therapies".

Questions are anchored on the synthetic lung-cancer case described in
[ideas/synthetic-clinical-notes.md](../ideas/synthetic-clinical-notes.md): a 68-year-old man
with COPD, emphysema, and coronary artery disease, eleven dated visits from 2025-01-10 to
2026-01-16, diagnosed with right-upper-lobe adenocarcinoma, treated with lobectomy and
adjuvant carboplatin/pemetrexed. The case is synthetic (LLM-generated) and lives in `data/`,
not in git. Dates below are the visit dates recorded in that case; events between visits are
known only to the precision the notes give.

Field definitions and the ID scheme are in [README.md](README.md).

## Easy

### CQ-CP-E01: What medications was the patient taking on 2025-03-20?

- **Why it is temporal**: medication facts have validity intervals; the answer is the set of
  intervals containing the date.
- **Minimal data**: for each medication, a start date and an end date (or open end), and the
  query date.
- **Expected answer**: a set. From the case: tiotropium, albuterol as needed, aspirin 81 mg,
  atorvastatin, metoprolol succinate, nitroglycerin as needed, budesonide-formoterol (started
  2025-02-07), nicotine patch (started 2025-02-07). Not oxycodone, acetaminophen, or
  ondansetron, which start later.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%).
- **A static KG gets this wrong because**: it returns the union of every medication ever
  recorded, including drugs started months later and drugs stopped months earlier.

### CQ-CP-E02: On what date was the lung malignancy tissue-confirmed, and at which visit was that result first recorded?

- **Why it is temporal**: a diagnosis has an onset of *knowledge*, distinct from the onset of
  the disease. The question asks for the former.
- **Minimal data**: the biopsy procedure with a date or date range; the visit at which its
  result was reviewed; the assertion "malignant cells confirmed" with a transaction time.
- **Expected answer**: a date or bounded interval plus a visit reference. From the case: the
  result was reviewed at the 2025-03-03 thoracic-oncology visit; the bronchoscopy itself is
  dated only as "approximately 1 month after the CT scan", so the procedure date is an
  interval, roughly late February 2025. A good answer states the precision.
- **Criterion**: Feasibility & Integration (15%): this is the kind of fact OMOP and FHIR
  already carry with dates, and the KG must round-trip it.
- **A static KG gets this wrong because**: "patient has adenocarcinoma" is asserted
  timelessly, so the question cannot be asked.

### CQ-CP-E03: How many days elapsed between the first primary-care visit for the new symptoms and the first cycle of adjuvant chemotherapy?

- **Why it is temporal**: a duration between two instants.
- **Minimal data**: the two visit dates.
- **Expected answer**: a duration. From the case: 2025-01-10 to 2025-06-06 is 147 days
  (about 21 weeks). The answer should also be computable as an interval if either endpoint
  were imprecise.
- **Criterion**: Feasibility & Integration (15%).
- **A static KG gets this wrong because**: without instants there is nothing to subtract. (This
  is the "diagnosis-to-treatment interval", a standard care-quality metric, which is why it
  belongs even though it is easy.)

## Medium

### CQ-CP-M01: Was adjuvant carboplatin/pemetrexed started after the right upper lobectomy, and how long after?

- **Why it is temporal**: ordering of two events plus a duration, where one event's date is
  only bounded. The surgery is not dated exactly: the preoperative cardiology visit is
  2025-03-20 and the postoperative inpatient visit is 2025-04-08.
- **Minimal data**: surgery date as an interval [2025-03-20, 2025-04-08]; chemotherapy start
  2025-06-06; the relation "adjuvant to".
- **Expected answer**: yes, with the gap as an interval of 59 to 78 days; the narrative's
  "roughly 6 to 8 weeks after surgery" is consistent with that. The answer must carry the
  uncertainty rather than pick a point.
- **Criterion**: Temporal Modeling Innovation (25%): representing an event whose time is known
  only to an interval, and propagating that through a duration.
- **A static KG gets this wrong because**: it can say both events happened but cannot order
  them or measure the gap; a naive date-stamped graph that assigns the surgery to a single
  guessed date reports false precision.

### CQ-CP-M02: As of 2025-01-24, which conditions were known for this patient, and which conditions in the final history must not appear in that answer?

- **Why it is temporal**: as-of reconstruction. Each condition has a date it became known
  (transaction time), separate from when it began (valid time).
- **Minimal data**: each condition with the visit at which it was first recorded.
- **Expected answer**: two sets. Known on 2025-01-24: COPD, emphysema, coronary artery disease,
  tobacco use disorder, hemoptysis, right upper lung opacity on chest imaging, unintentional
  weight loss. Must not appear: spiculated right upper lobe mass (CT reviewed 2025-02-07),
  tissue-confirmed malignancy (2025-03-03), everything postoperative.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%): this is the plainest
  no-leakage test the data supports.
- **A static KG gets this wrong because**: the final condition list is all it has; it would
  "know" the cancer at the first visit.

### CQ-CP-M03: Which medications were started and later stopped during the case, with their intervals, and which were interrupted and resumed?

- **Why it is temporal**: validity intervals, including gaps (a medication held and resumed is
  two intervals for one drug).
- **Minimal data**: medication start and stop events per visit, including "hold" and "resume".
- **Expected answer**: a table of drug, interval(s), reason. From the case: prednisone and
  azithromycin, five-day courses from 2025-01-10; oxycodone from the surgical admission
  (bounded by 2025-04-08) tapering after 2025-05-02; ondansetron 2025-06-06 to 2025-10-10;
  aspirin held perioperatively and resumed 2025-05-02; nicotine patch 2025-02-07 onward with
  dose steps 21 mg, 14 mg, 7 mg.
- **Criterion**: Temporal Modeling Innovation (25%): one drug, several intervals, with a dose
  that changes across them.
- **A static KG gets this wrong because**: a drug is either "a medication of" the patient or
  not; interruptions, tapers, and dose changes are invisible.

### CQ-CP-M04: Did the care sequence follow the expected order (imaging before tissue diagnosis before staging before cardiac clearance before resection before adjuvant therapy before surveillance), and which pairs, if any, violate it?

- **Why it is temporal**: a partial order over event types, checked against actual event
  instants or intervals using `precedes` / `time:intervalBefore`.
- **Minimal data**: dated events typed with a pathway vocabulary (NCIT or SNOMED procedure
  concepts), and the expected partial order as axioms.
- **Expected answer**: a list of ordered pairs with the relation found (before, overlaps,
  unknown because of imprecision) and any violations. From the case: no violations; some pairs
  are "before" only within the precision of the bounding visits.
- **Criterion**: Ontology Rigor & Interoperability (20%): the expected order is a set of
  machine-checkable axioms over RO/OWL-Time relations, not a comment.
- **A static KG gets this wrong because**: events have no order, so a pathway is just a bag of
  procedures.

## Hard

### CQ-CP-H01: On 2025-01-24, using only facts recorded on or before that date, what was the differential diagnosis, and was ordering an urgent chest CT concordant with the guideline version in force on that date?

- **Why it is temporal**: no-leakage reasoning plus guideline versioning. The guideline that
  applies is the one whose validity interval contains the visit date, and the facts available
  are those with transaction time at or before the visit.
- **Minimal data**: the as-of patient state from CQ-CP-M02; a guideline KG with versioned
  recommendations (for example, recommendations on evaluating hemoptysis in a smoker over 40
  with an abnormal radiograph), each with a validity interval and a source.
- **Expected answer**: the differential as recorded at that visit (COPD flare, bronchitis,
  pulmonary malignancy, pneumonia less likely, musculoskeletal pain, embolism unlikely,
  cardiac ischemia) and a boolean "concordant" with the recommendation cited and its validity
  interval shown. The derivation must list every fact used and its transaction time.
- **Criterion**: Reasoning Correctness & Temporal Consistency (25%); secondary Workflow
  Relevance (15%).
- **A static KG gets this wrong because**: it would evaluate the decision against the current
  guideline using facts that were not yet known, and it cannot show which facts it used when.
- **Data needed that we do not have**: a versioned guideline source. Candidates are noted in
  [resources/README.md](../resources/README.md); none has been ingested.

### CQ-CP-H02: Did the adjuvant chemotherapy satisfy its preconditions at the time it started, namely a completed resection with pathology showing a recurrence risk that warrants it, and would the graph detect a hypothetical case in which the same regimen was started before the pathology result?

- **Why it is temporal**: sequential, non-interchangeable therapy. "Adjuvant" is defined by its
  position after a definitive local treatment and its dependence on that treatment's result.
- **Minimal data**: resection event (interval), pathology report with result date, adjuvant
  therapy start, and axioms: an adjuvant therapy `preceded by` a resection; the pathology
  result's valid-from date precedes the therapy start.
- **Expected answer**: for the real case, "yes" with the chain of dated facts; for the
  corrupted case, a reasoner report naming the unsatisfiable class or inconsistent individual.
  Both outputs should come from a standard reasoner (ROBOT, whelk, HermiT), not bespoke code.
- **Criterion**: Ontology Rigor & Interoperability (20%); secondary Reasoning Correctness
  (25%).
- **A static KG gets this wrong because**: "patient received carboplatin" and "patient had
  lobectomy" coexist with no order, so neoadjuvant and adjuvant are indistinguishable, and the
  impossible case is not impossible.

### CQ-CP-H03: Across a cohort of synthetic patients with resected non-small-cell lung cancer treated between 2019 and 2025, which were treated under a standard of care that has since changed, and for whom would the current standard recommend something different?

- **Why it is temporal**: evidence and guideline evolution over a cohort. Real examples of
  changes in this period include the regulatory approvals of adjuvant osimertinib for
  EGFR-mutated disease (December 2020), adjuvant atezolizumab (October 2021), and adjuvant
  pembrolizumab (January 2023) for resected non-small-cell lung cancer; the exact dates and
  eligibility criteria should be taken from the regulatory record, not from this file.
- **Minimal data**: per patient, resection date, stage, biomarker status, adjuvant regimen and
  start date; a KG of recommendations and approvals with validity intervals and eligibility
  conditions.
- **Expected answer**: a partition of the cohort (treated under a still-current standard;
  treated under a superseded standard; treated under a superseded standard and would now be
  recommended a different regimen), with the recommendation versions cited.
- **Criterion**: Clinical Workflow Relevance & Impact (15%): this is a tumor-board and
  quality-improvement question with a decision attached (who should be re-evaluated).
  Secondary Temporal Modeling (25%) for evidence evolution.
- **A static KG gets this wrong because**: it holds one recommendation per condition, so every
  patient is either concordant or not with today's guidance, which is the wrong question.
- **Data needed that we do not have**: a cohort (the synthetic generator can produce one) and
  a versioned guideline or approvals KG.
