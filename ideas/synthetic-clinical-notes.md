# Synthetic clinical notes as longitudinal test data

## What it is

Matt Satusky's **clinical-notes-generation** project
(<https://github.com/satusky/clinical-notes-generation>, MIT license) is a multi-agent LLM
pipeline that generates synthetic clinical cases. From its README:

- A **case-building** phase turns coded variables (for example NAACCR cancer-registry codes) and
  knowledge-source documents into a `CaseConfig`, via parallel "investigator" agents.
- A **note-generation** phase runs a Narrator, an Orchestrator that builds the visit timeline,
  and a per-visit Coordinator / Clinician / Scribe loop. An **information barrier** keeps the
  note-writing Clinician agent unaware of the true diagnosis, so early notes contain the
  uncertainty a real clinician would have. The Scribe updates the patient's medical history
  after each visit.
- Options include case type (for example chronic) and outcome (for example worsening).

An example output is saved locally at `data/matt-synthetic-case/997ccaf0.html` (not committed;
it is a colleague's example output and the licence of generated outputs is not stated). It is a
68-year-old man with COPD, emphysema, and coronary artery disease who develops invasive
adenocarcinoma of the right upper lobe. The case has:

- A free-text narrative covering roughly a year from first symptoms.
- **Eleven dated visits** from 2025-01-10 to 2026-01-16 across primary care, pulmonology,
  thoracic oncology, cardiology, thoracic surgery, and medical oncology.
- Per-visit structured sections: symptoms, vitals, exam findings, tests ordered, treatments,
  known conditions, current medications, relevant history, and a "disease progression" note
  describing what is really happening (the ground truth the Clinician agent did not see).
- A **final medical history** with the end-state condition list and medication list, which
  differs from the visit-1 lists (for example budesonide-formoterol and a nicotine patch
  appear, oxycodone appears and is later tapered, aspirin is held perioperatively then resumed).

## Why it is relevant to time in KGs

The case is a ready-made specimen of every temporal phenomenon the challenge text lists:

- **Event sequencing**: symptoms, empiric treatment, chest X-ray, CT, PET-CT, bronchoscopy with
  EBUS, tumor board, cardiac clearance, lobectomy, adjuvant carboplatin/pemetrexed,
  surveillance CT, in that order and with stated gaps ("within 2 weeks", "about 6 weeks after
  tissue diagnosis").
- **Validity intervals**: medications with start and stop dates; a chest tube that is present
  at one visit and removed by the next; a differential diagnosis that is valid only until the
  biopsy result.
- **Evolving evidence**: the diagnosis moves from "presumed COPD flare" through "suspicious
  opacity" and "spiculated mass" to "tissue-confirmed adenocarcinoma"; each stage is the best
  available knowledge on its date.
- **Sequential, non-interchangeable therapies**: adjuvant chemotherapy is appropriate only
  after resection with a particular pathology result; the same drugs given before surgery would
  be a different (neoadjuvant) decision. This is exactly the "care pathways with sequential,
  non-interchangeable therapies" domain NIH names.
- **Known ground truth**: because the generator knows the diagnosis and the per-visit "disease
  progression", every "what was known at time T?" question has a checkable answer, and so does
  every "what was actually true at time T?" question. That pairing is what a no-temporal-leakage
  test needs.

## Which judging criteria it serves

- **Clinical Workflow Relevance & Impact (15%)**: lung-cancer diagnostic and adjuvant-therapy
  pathway, with concrete decision points (work up hemoptysis in a smoker; proceed to surgery
  given cardiopulmonary risk; start adjuvant therapy given pathology).
- **Reasoning Correctness & Temporal Consistency (25%)**: supplies the as-of questions and
  their answers.
- **Phase 2 Demonstrated Temporal Reasoning (30%) and Evaluation Rigor (20%)**: a natural
  **static baseline** is the same case loaded as a flat KG where all eleven visits' facts are
  asserted without time. Many questions then come out wrong or contradictory (the patient is
  simultaneously on and off aspirin; the differential includes and excludes malignancy), and
  the six required metrics can be computed on both graphs.
- Indirectly, **Feasibility & Integration (15%)**: the structured per-visit sections map onto
  OMOP / FHIR concepts (Condition, MedicationStatement, Procedure, Observation) and onto Biolink
  categories, which is the integration story.

## Gaps and risks against the rubric

- **It supplies data, not a model.** On its own it earns nothing under Temporal Modeling
  Innovation (25%) or Ontology Rigor (20%). It needs a representation and an ontology from
  elsewhere.
- **Synthetic realism.** NIH asks for "realistic biomedical data or scenarios", which this
  satisfies, but the write-up must say the data is synthetic and must not imply validation on
  real patients. The generator's own fidelity (does it produce guideline-concordant timelines?)
  is an open question to ask its author.
- **LLM-generated text needs extraction.** The structured sections reduce the burden, but
  dates inside the narrative ("about 6 weeks after tissue diagnosis") are relative and would
  need normalization. The i2b2 2012 and THYME corpora show how hard clinical temporal
  extraction is; keep extraction out of the critical path by using the structured sections.
- **One case is an anecdote.** A benchmark needs tens to hundreds of cases with varied
  outcomes. The generator can produce them, but we have not run it and do not know the cost
  per case.
- **Licensing of outputs.** The code is MIT; the licence of generated cases, and of the
  knowledge sources they draw on, should be confirmed before any case is committed.

## Smallest useful experiment

1. Hand-convert the one example case to a small temporal KG, in Turtle, using Biolink
   categories for nodes, Biolink associations with `temporal_interval_qualifier` for facts that
   have validity intervals, OWL-Time intervals for the dates, and PROV-O timestamps for when
   each fact became known. Expect on the order of a few hundred triples.
2. Produce the **static baseline** mechanically by dropping every temporal triple.
3. Write SPARQL for the care-pathway competency questions
   ([competency-questions/care-pathways.md](../competency-questions/care-pathways.md)) and run
   them against both graphs. Record which answers differ and why.
4. Add a handful of OWL axioms (for example "adjuvant therapy must start after the resection
   it is adjuvant to") and check with ROBOT or whelk that the temporal graph is consistent and
   that a deliberately corrupted graph is not.

Everything in steps 1 to 4 can live in `ideas/synthetic-clinical-notes/` once it exists; the
source case stays in `data/`.

## Open questions

- Does the generator emit a structured (JSON) form of the case alongside the HTML? The README
  mentions an `--output` flag but not the format. A JSON export would make step 1 scriptable.
- Can the Orchestrator's visit timeline be exported directly as ground-truth intervals?
- How many cases, and with what outcome mix, would make a credible Phase 2 benchmark?
- Would the author be willing to generate a batch under an explicit open licence for the
  challenge?
