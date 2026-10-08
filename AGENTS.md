# AGENTS.md

Guidance for coding agents (and humans) working in this repository.

## What this repo is for

This repo is exploratory scaffolding for the NIH Office of Data Science Strategy (ODSS) prize
competition **"It's About Time: Temporal Reasoning in Biomedical Knowledge Graphs"**:

- Challenge page: <https://www.nih.gov/challenges/its-about-time-temporal-reasoning-biomedical-knowledge-graphs-challenge>
- Competition site (registration, moderated Q&A forum, submission portal):
  <https://work.crowdplat.com/challenge/nih-temporal-knowledge-graph-challenge>

The immediate goal is **not** to write the submission. It is to make the problem legible enough,
and to show enough connections to existing RENCI (<https://renci.org/>) knowledge-graph tooling,
that colleagues want to lead or join an entry. Everything here should help a reader answer
"what would a winning entry have to do, and what do we already have that helps?"

`nih.gov` blocks automated fetches (Cloudflare 403). A saved copy of the challenge page lives
in `data/` (gitignored); read that instead of retrying the fetch.

## The challenge in one screen

Two phases. Only Phase 1 winners may enter Phase 2.

| | Phase 1: Concept Design & Feasibility | Phase 2: Prototype & Demonstration |
|---|---|---|
| Submissions open | 2026-10-05 | 2027-04-05 |
| Submissions close | 2027-01-15 (Pacific Time) | 2027-11-12 |
| Winners announced | 2027-03-15 | 2028-02-18 |
| Prizes | up to 10 x $25,000 | $350,000 / $250,000 / $150,000 |

**Phase 1 deliverables**

1. A **10-page PDF** (11-point font or larger, at most 15 characters per inch, at most 6 lines
   per vertical inch; Arial, Georgia, Helvetica, Palatino recommended).
2. An **ontology file, at most 3 MB**, in OWL/RDF (Turtle or RDF/XML) or OBO format. It may be
   the ontology we plan to use or an *excerpt* that shows how the approach represents and
   reasons over temporal biomedical knowledge. NIH's illustrative example is a toy with
   abstract classes and two reasoner-checkable axioms (see
   [resources/README.md](resources/README.md)); it sets a low bar that we should clear by a lot.

**Phase 1 judging criteria** (each scored 1 to 5, then weighted)

| Weight | Criterion | What the rubric text actually asks for |
|---|---|---|
| 25% | Temporal Modeling Innovation | Representation of events, sequences, durations, validity intervals, evidence evolution, uncertainty; **temporal embeddings** are named explicitly; technical rigor of dynamic-graph modeling |
| 25% | Reasoning Correctness & Temporal Consistency | Inference uses only information available at query time (**no temporal leakage**); respects event ordering and validity intervals |
| 20% | Ontology Rigor & Interoperability | Ontology in a logic-capable format (OWL or other DL/FOL); **consistent with the Biolink Model**; reuses NLM or OBO ontologies; **machine-verifiable axioms beyond the class hierarchy** |
| 15% | Feasibility & Integration | Can produce a semantically rich integrated KG; integrates with existing ontologies, standards, infrastructure |
| 15% | Clinical or Public-Health Workflow Relevance & Impact | A **specific** clinical or public-health workflow; execution would change decisions and measurably improve outcomes |

**Phase 2 judging criteria**

| Weight | Criterion | Notes |
|---|---|---|
| 30% | Demonstrated Temporal Reasoning | On realistic data; measured on **shared benchmark tasks and test data**, not presentation |
| 30% | Correctness of Inference | Temporal consistency; no fact asserted before its supporting evidence holds; no validity-interval violations |
| 20% | Evaluation Rigor | Head-to-head vs a **defined static-KG baseline**. Required metrics: logical inconsistencies / unsatisfiable classes, number of triples, relationship richness, attribute richness, class/property instantiation ratio, interlinking completeness |
| 20% | Extensibility | Reusable in other biomedical domains; documentation and artifacts |

Phase 2 also expects runnable code with pinned environments, datasets, documentation, compute
specs, and a recorded walk-through.

**Domains NIH names as high-impact**: care pathways with sequential, non-interchangeable
therapies; infectious-disease surveillance; pharmacovigilance. NIH will provide **no data and no
benchmark** in Phase 1; participants supply their own. **No protected health information (PHI).**

## Score against the rubric, not against our interests

The maintainer has said plainly: their habit in challenges like this is to bend the problem
toward questions they personally find interesting rather than toward what will score. Agents
working here are asked to **push back when that happens**.

Concretely, when an idea, competency question, or experiment is proposed, ask and answer:

- Which Phase 1 criterion does this serve, and at what weight? If the honest answer is "none
  directly", say so in the document rather than letting it pass.
- Is the representation **Biolink-consistent** and does it reuse OBO/NLM ontologies?
- Does it produce **OWL axioms a reasoner can check** (equivalence to restrictions,
  disjointness, covering axioms, property chains, cardinality), not just a class tree or a
  LinkML schema?
- Does the reasoning avoid **temporal leakage**, i.e. could we show that an inference about time
  T used only facts known at T?
- Is there a **specific clinical or public-health workflow** and a decision it would change?
- Could it be compared against a **static-KG baseline** on the six Phase 2 metrics?

Things that are intellectually attractive but score poorly on their own include: temporal KG
embedding methods with no ontology, molecular-biology causal modeling with no clinical workflow,
and general-purpose knowledge-representation elegance with no use case. They can still be
*parts* of an entry; the write-up must say which part of the rubric they carry.

## Public-repo rules

This repository is public on GitHub. Before committing anything, check:

- **Nothing goes into git that can't be shared publicly or cited by URL.** Downloaded web pages,
  colleagues' example outputs, files with unclear licensing, and anything shared privately stay
  in `data/`, which is gitignored. Instructions for *obtaining* such files belong in
  `resources/README.md` with a target path under `data/<name>/`.
- **No PHI, ever.** Use synthetic or openly licensed data, and label synthetic data as synthetic
  everywhere it appears.
- **Data a public source lets anyone download, without login or terms, is already public.**
  Keep it under `data/`, and check small excerpts into the repo when a document needs them,
  citing the source and the snapshot date. If some of it looks like a confidentiality breach
  (names, contact details, anything the source would not knowingly publish), don't commit it;
  open an issue here on the `Upstream` milestone so it can be reported to the source.
- **Name people only alongside their public work.** It is fine to say that a colleague built a
  publicly available tool and link to it. Do not attribute private conversations, unpublished
  plans, or opinions to anyone.
- Scratch outputs, intermediate results, and local notes belong in `data/` or the agent's
  scratchpad, not in the tree.

## Repo layout

```
AGENTS.md                 this file
README.md                 short orientation
ideas/                    one Markdown file per idea; promote to ideas/<name>/ when it needs scripts or several files
competency-questions/     what a successful temporal KG must be able to answer, by domain and difficulty
resources/                annotated links to graphs, standards, tooling, and papers; download instructions for data/
tools/                    Scala CLI scripts (dependencies declared inline), e.g. check-owl.scala for strict parsing and reasoning
data/                     gitignored scratch and downloaded material
```

## Conventions

- **Competency questions** (CQs) have stable IDs `CQ-<domain>-<E|M|H><nn>`, where the domain is
  `CP` (care pathways), `ID` (infectious-disease surveillance), `PV` (pharmacovigilance), or `XX`
  (cross-cutting). Difficulty is E (easy), M (medium), or H (hard). Each CQ records: the
  question, why it is temporal, the minimal data needed, the expected answer shape, the Phase 1
  criterion it exercises, and what a static KG gets wrong. See
  [competency-questions/README.md](competency-questions/README.md). Do not renumber IDs; retire
  an ID rather than reuse it.
- **Dates** in ISO 8601 (`2026-10-07`). Durations as ISO 8601 durations (`P6W`) when precision
  matters.
- **Terms**: prefer Biolink, OBO (RO, MONDO, HP, CHEBI, NCIT, OAE, etc.), and OWL-Time terms,
  and cite them as CURIEs or full IRIs (e.g. `RO:0002090`, `time:intervalBefore`).
- **Scripts**: declare dependencies in the file so nothing needs a project-wide build. Python
  scripts and marimo notebooks use a PEP 723 header and run with `uv run` (or
  `uvx marimo edit --sandbox` for notebooks); JVM scripts use Scala CLI `//> using`
  directives (see [tools/README.md](tools/README.md)). Downloaders write under `data/`,
  skip files already present, and record the source's snapshot or export date.
- **Commits**: small, one topic each, so colleagues can review the rules, resources, ideas, and
  CQs separately. If an approach was tried and failed, record it in the commit message, and in
  the relevant document if someone is likely to try it again.
- **Pull requests**: the maintainer reviews and merges. Agents open PRs but do not merge.

## Eligibility footnotes worth remembering

Flagged here so nobody is surprised later; not legal advice.

- Federal grant or cooperative-agreement funds, and federal contract funds, may not be used to
  develop a submission.
- Federal employees acting within the scope of their employment are ineligible; HHS employees
  are ineligible in any capacity.
- Cash prizes go only to U.S. citizens, permanent residents, or U.S.-incorporated entities.
  Others may participate as team members and be recognized.
- One prize per participant or team per phase.
