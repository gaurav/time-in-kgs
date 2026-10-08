# Ideas

Candidate approaches and ingredients for an entry, each scored honestly against the judging
rubric in [AGENTS.md](../AGENTS.md). An idea lives in a single Markdown file until it needs
scripts or several files, at which point it becomes a directory `ideas/<name>/` with its own
README.

Every idea file uses the same headings so they can be compared side by side:

1. **What it is** (with public links)
2. **Why it is relevant to time in KGs**
3. **Which judging criteria it serves**
4. **Gaps and risks against the rubric**
5. **Smallest useful experiment**
6. **Open questions**

## Current ideas

| Idea | One line | Criteria it mainly serves | Distance from the rubric |
|---|---|---|---|
| [Synthetic clinical notes as test data](synthetic-clinical-notes.md) | Use an LLM-generated, PHI-free longitudinal case as the data for care-pathway questions and as the basis of a static-vs-temporal comparison | Workflow Relevance (15%), Reasoning Correctness (25%), Phase 2 Demonstrated Reasoning and Evaluation Rigor | Close. Supplies data and a use case; does not by itself supply a temporal model or ontology |
| [GO-CAM causal models](go-cam-causal-models.md) | Borrow the OWL/RO-backed causal-model curation stack and ask what it takes to add validity intervals and ordering axioms | Ontology Rigor (20%), Temporal Modeling (25%), Feasibility & Integration (15%) | Medium. Strong on axioms and infrastructure; the molecular use case is far from a clinical workflow, so it must be the engine, not the story |
| [Wikidata qualifiers](wikidata-qualifiers.md) | Treat Wikidata's statement qualifiers and ranks as a proven large-scale pattern for "what was true when", and compare it with OWL-Time and RDF-star | Temporal Modeling (25%), Feasibility & Integration (15%) | Medium. Good representation pattern and a familiar reference point; weak on inference and not biomedical |
| [Veterinary adverse events](veterinary-adverse-events/README.md) | Use openFDA's animal adverse-event reports and the Integrated Canine Data Commons as small, public, PHI-free data with real timestamps for the pharmacovigilance and care-pathway questions, with scripts and a notebook | Reasoning Correctness (25%), Feasibility & Integration (15%), Phase 2 Demonstrated Reasoning | Medium. Supplies data and a leakage demonstration; the workflow is veterinary, so the clinical-relevance case has to be made through comparative oncology or by swapping in human FAERS |

## How these could fit together

A plausible entry uses the three as layers rather than alternatives:

- **Data and workflow**: synthetic longitudinal cases (care pathways), plus public
  pharmacovigilance and surveillance data, framed around a specific decision a clinician or
  epidemiologist makes.
- **Representation**: Biolink associations linked to OWL-Time intervals, with provenance
  timestamps in PROV-O. Biolink's `temporal_interval_qualifier` is string-valued as published,
  so this needs an extension or a proposed Biolink change (see
  [resources](../resources/README.md#standards-the-rubric-names-or-implies)). The Wikidata comparison explains the design choice.
- **Reasoning and verification**: OWL axioms over RO/OWL-Time relations that make impossible
  orderings unsatisfiable, checked with the same reasoners the GO-CAM and Ubergraph stacks use,
  so the "unsatisfiable classes" metric is produced by standard tooling.

That sketch is a hypothesis, not a plan. The
[competency questions](../competency-questions/README.md) are the test of whether any layer earns
its place.

## Ideas considered and parked

Listed so nobody re-derives them from scratch. Any of them can be revived if a competency
question demands it.

- **Temporal KG embeddings as the core contribution.** The rubric names "temporal embeddings",
  but 20% of Phase 1 is OWL rigor and 25% is reasoning correctness with no leakage, both of
  which embeddings alone cannot demonstrate. Embeddings may appear as a component (e.g. for
  link prediction over the temporal graph) but not as the entry's spine.
- **Molecular causal pathways as the use case.** Interesting, and close to GO-CAM, but the 15%
  Workflow Relevance criterion asks for a clinical or public-health workflow and a decision
  that changes. Keep the molecular work as infrastructure.
- **Building a new temporal ontology from scratch.** Duplicates OWL-Time, RO, BFO, CNTRO, and
  TEO, and loses points on interoperability. Extend, don't replace.
- **Anything requiring real patient data.** No PHI is allowed, and credentialed datasets such
  as MIMIC cannot be redistributed. Synthetic or open data only.
