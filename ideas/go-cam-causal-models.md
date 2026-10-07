# GO-CAM causal models and the Noctua stack

## What it is

**GO-CAMs** (Gene Ontology Causal Activity Models, <https://geneontology.org/docs/gocam-overview/>)
link standard GO annotations into causal networks. Each node is a molecular activity that is
`enabled_by` a gene product, `occurs_in` a cellular component, and is `part_of` a biological
process. Activities are linked by Relations Ontology (RO) causal relations such as
`RO:0002629` directly positively regulates, `RO:0002630` directly negatively regulates, and
`RO:0002413` directly provides input for.

The curation stack is **Noctua** (<https://github.com/geneontology/noctua>), backed by Minerva,
an OWL-based model store that uses an OWL reasoner during editing. Models are versioned in
<https://github.com/geneontology/noctua-models>; the schema and a Python library are in
<https://github.com/geneontology/gocam-py> (LinkML, with a GO-CAM JSON format). Jim Balhoff has
worked on this stack and on the reasoning tooling around it (whelk, relation-graph; see
[resources/README.md](../resources/README.md)).

## Why it is relevant to time in KGs

GO-CAMs encode **causality without explicit time**. That is both the attraction and the gap:

- A causal chain implies a **partial temporal order**: if activity A directly positively
  regulates activity B, then A's effect on B cannot precede A. The challenge text asks for
  "time-respecting causal paths" and warns against "temporally impossible inference paths";
  GO-CAMs are a large, curated corpus of causal paths on which to define what "time-respecting"
  means and to test whether a reasoner can enforce it.
- The stack already does what the Ontology Rigor criterion asks: models are OWL individuals and
  axioms, validated against RO and GO with a reasoner at curation time, with provenance
  (contributor, date, evidence codes, publications) on every assertion. Adding
  **validity intervals** (OWL-Time) and **ordering axioms** (RO temporal relations, with
  BFO's `precedes`) is an extension of an existing pattern, not a new system.
- The models are small (tens to a few hundred assertions), public, versioned in git, and have
  evidence attached, which makes them a tractable place to demonstrate **evidence evolution**:
  a model revised when a paper is retracted or superseded is a worked example of "what was once
  true".

## Which judging criteria it serves

- **Ontology Rigor & Interoperability (20%)**: OWL, OBO relations, machine-checkable axioms, a
  reasoner in the loop, and Biolink mappings for GO and RO already exist in Ubergraph.
- **Temporal Modeling Innovation (25%)**: the specific innovation is deriving and checking
  temporal constraints from causal structure, and representing the point at which each causal
  assertion became supported.
- **Feasibility & Integration (15%)**: a demonstrated curation workflow, model store, and
  reasoning pipeline that colleagues know how to run.

## Gaps and risks against the rubric

- **Not a clinical or public-health workflow.** The 15% Workflow Relevance criterion will score
  a molecular-biology use case poorly unless it is tied to a decision someone makes about
  patients or populations. GO-CAM should be presented as the **reasoning and curation engine**,
  with the use case coming from care pathways, surveillance, or pharmacovigilance. A causal
  chain of clinical events (exposure, onset, treatment, response) is structurally a GO-CAM with
  different node types, and that is the pitch.
- **Causal order is not temporal order.** Regulation can be continuous, cyclic, or
  simultaneous; "A regulates B" does not give durations or dates. The ordering we can derive is
  a constraint, not a timeline. Over-claiming here would hurt under Reasoning Correctness.
- **OWL DL limits.** Interval composition (Allen's algebra) is not fully expressible in OWL DL;
  some constraints will need rules (SWRL, SHACL, Datalog) or a dedicated temporal reasoner.
  This is a general issue for any OWL-based entry and the GO-CAM stack does not solve it.
- **Molecular vocabulary does not transfer by itself.** Relevant node types for a clinical
  causal model (disease, drug exposure, adverse event, procedure) come from MONDO, CHEBI /
  RxNorm, OAE, NCIT, not from GO.

## Smallest useful experiment

1. Pick one small public GO-CAM from noctua-models (a linear signalling cascade of five to ten
   activities).
2. Add to each causal edge an OWL-Time interval for the activity it connects, plus a PROV-O
   `generatedAtTime` for when the supporting evidence was published.
3. State the ordering axioms (for example, a direct regulation edge implies the regulator's
   activity interval `time:intervalBefore` or `time:intervalOverlaps` the regulated activity's
   interval; a cycle without overlap is unsatisfiable).
4. Run whelk or ROBOT `reason`; show the consistent model, then corrupt one interval and show
   the unsatisfiable class or inconsistent individual.
5. Repeat steps 2 to 4 with the **same relations over a clinical causal chain** taken from the
   synthetic lung-cancer case (smoking exposure causally upstream of adenocarcinoma; resection
   causally upstream of recurrence-free surveillance), to show the pattern transfers.

## Open questions

- Which RO temporal relations are already used in GO or other OBO ontologies, and do they carry
  the characteristics (transitivity, inverses) we would rely on?
- Does Minerva's reasoning mode support the axioms we would add, or would we check them offline?
- Is there a published analysis of how GO-CAMs change over time (noctua-models git history)
  that could serve as the "evidence evolution" dataset?
- Would the GO-CAM team be interested in temporal annotations as a feature, independent of the
  challenge?
