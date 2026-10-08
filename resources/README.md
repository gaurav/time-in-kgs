# Resources

Annotated links. Each entry says why it matters for the challenge, and which judging criterion
it mostly speaks to (see the rubric in [AGENTS.md](../AGENTS.md)). Everything here is public and
citable by URL. Anything that has to be downloaded gets a target path under `data/`, which is
gitignored.

## The challenge itself

- **Challenge page** (NIH ODSS):
  <https://www.nih.gov/challenges/its-about-time-temporal-reasoning-biomedical-knowledge-graphs-challenge>.
  Authoritative text for phases, deliverables, rubric, and rules. `nih.gov` returns a Cloudflare
  403 to automated fetches; save the page in a browser to
  `data/` and read the saved copy.
- **Competition site** (CrowdPlat):
  <https://work.crowdplat.com/challenge/nih-temporal-knowledge-graph-challenge>. Registration,
  the moderated public Q&A forum (the single official channel for questions), and the
  submission portal. Registering is free and is the only way to read the Q&A.
- **NIH's illustrative OWL example**: <https://www.nih.gov/node/23566> (download by hand to
  `data/challenge-owl/ItsAboutTime.owl`). A roughly 5 KB RDF/XML file with seven abstract
  classes (`A`..`G`), three unlabeled object properties, no imports, and no temporal content.
  Its value is that NIH marks two axioms as examples of "machine-verifiable axioms beyond the
  class hierarchy": an equivalence to an existential restriction plus a disjointness
  (`C ≡ p some (E and (A or B))`, `C disjointWith D`) and a covering axiom (`E ≡ F or G`). Read
  it as a statement of the *minimum* the Ontology Rigor criterion (20%) expects. **The file is
  not valid RDF/XML as published**: its two explanatory comments are wrapped in literal
  parentheses outside the XML comment markers (lines 76 and 111), and RDF/XML allows only
  whitespace between node elements. Checked 2026-10-07 with
  [`tools/check-owl.scala`](../tools/check-owl.scala): strict Jena 5.2.0 rejects it
  ("Non-whitespace text content between element tags"), and so does the OWL API 4.5.29's own
  RDF/XML parser ("Expecting an object element instead of character content"). It loads in
  ROBOT and Protégé only because the OWL API then falls back to RDF4J Rio's more lenient
  RDF/XML parser, and rdflib 7.6.0 silently drops the stray text. Removing the parentheses
  makes it pass every parser, with the same 49 triples and 5 logical axioms; HermiT finds it
  consistent with no unsatisfiable classes. Don't copy its layout by hand, and run our own
  ontology file through a strict parser before submitting.

## Knowledge graphs and tooling built at or with RENCI

- **Ubergraph** <https://github.com/INCATools/ubergraph>, SPARQL endpoint
  <https://ubergraph.apps.renci.org/sparql>. About forty mutually referential OBO ontologies
  (Uberon, CL, GO, HP, MP, MONDO, ChEBI, RO, NCBITaxon, PRO, and others) in one Blazegraph
  store, with precomputed OWL classification, materialized existential relations, redundant and
  non-redundant closure graphs, and an RDF rendering of Biolink with OBO terms mapped to Biolink
  categories. *Why it matters*: the Biolink-plus-OBO backbone the rubric asks for already
  exists and is queryable; temporal relations from RO and BFO are in it. Criteria: Ontology
  Rigor, Feasibility & Integration.
- **relation-graph** <https://github.com/INCATools/relation-graph> and **whelk**
  <https://github.com/balhoff/whelk>. Tools (by Jim Balhoff and collaborators) that materialize
  existential relations over OWL ontologies and provide a fast OWL EL reasoner. *Why it
  matters*: if we add temporal ordering axioms to an ontology, these are the tools that would
  check them at scale and feed the "unsatisfiable classes" metric in Phase 2.
- **ROBOKOP** <https://robokop.renci.org/>, GitHub <https://github.com/RobokopU24>. A
  Biolink-compliant biomedical KG built from public sources by the ORION ingest pipeline, with a
  question-answering UI and an API. *Why it matters*: a large static Biolink KG is exactly the
  kind of baseline the Phase 2 rubric wants a temporal approach compared against. Also a
  reminder that ROBOKOP edges carry provenance and publication lists but, like most KGs, no
  validity intervals. Criteria: Feasibility & Integration, Evaluation Rigor.
- **Open Knowledge Network (Proto-OKN)** <https://okn.us/>, registry and federated query
  (FRINK) <https://registry.okn.us/>, GitHub <https://github.com/frink-okn>. NSF-funded network
  of forty-plus themed graphs (biomedical ones include SPOKE-OKN, BioBricks, Bio-Health KG,
  FDA MAUDE, Rare Disease KG) federated through infrastructure run at RENCI. *Why it matters*:
  shows how an integrated KG is assembled and queried across sources; FDA MAUDE and SPOKE are
  plausible pharmacovigilance inputs. Criteria: Feasibility & Integration.
- **Babel / Node Normalization** <https://github.com/TranslatorSRI/Babel>,
  <https://github.com/TranslatorSRI/NodeNormalization>. Identifier normalization across
  biomedical vocabularies. *Why it matters*: any integrated temporal KG needs to resolve the
  same drug, disease, or phenotype across sources; this is the piece that does it.
- **NCATS Biomedical Data Translator and TRAPI** <https://github.com/NCATSTranslator/ReasonerAPI>.
  The query API that ROBOKOP and the Translator ecosystem speak. *Why it matters*: Biolink
  association-level qualifiers, including temporal ones, are how TRAPI would carry time.
- **GO-CAM / Noctua stack**: GO-CAM overview <https://geneontology.org/docs/gocam-overview/>,
  Noctua <https://github.com/geneontology/noctua>, models
  <https://github.com/geneontology/noctua-models>, LinkML schema and Python library
  <https://github.com/geneontology/gocam-py>. Curated causal activity models linked with RO
  relations such as `RO:0002629` (directly positively regulates), `RO:0002630` (directly
  negatively regulates), and `RO:0002413` (directly provides input for). Jim Balhoff has worked
  on this stack. *Why it matters*: a mature, OWL-backed curation workflow for *causal* models;
  see [ideas/go-cam-causal-models.md](../ideas/go-cam-causal-models.md).
- **Synthetic clinical notes generator** <https://github.com/satusky/clinical-notes-generation>
  (Matt Satusky, MIT license). Multi-agent LLM pipeline that builds a case configuration, a
  visit timeline, per-visit notes, and a scribe-maintained history, with an information barrier
  so the note writer does not know the diagnosis. An example output is in
  `data/matt-synthetic-case/` (not committed). *Why it matters*: PHI-free longitudinal cases
  with known ground truth; see
  [ideas/synthetic-clinical-notes.md](../ideas/synthetic-clinical-notes.md).

## Standards the rubric names or implies

- **Biolink Model** <https://biolink.github.io/biolink-model/>. Named in the Ontology Rigor
  criterion. Already has association-level slots
  [`temporal_context_qualifier`](https://biolink.github.io/biolink-model/temporal_context_qualifier/)
  (a time constraint on the truth value of an association) and its child
  [`temporal_interval_qualifier`](https://biolink.github.io/biolink-model/temporal_interval_qualifier/).
  **Neither can point at an OWL-Time interval.** Checked 2026-10-07 against release v4.4.5
  (unchanged on `master` at `a4180f8`):
  - `temporal_interval_qualifier` declares no range, so it inherits `time type` from its parent.
    That is a literal type (`uri: xsd:string`, `typeof: time`, described as "a lexical
    representation of xsd:time", which is a time of day), not a class.
  - The generated OWL makes both slots `owl:DatatypeProperty`, and `temporal_context_qualifier`
    has `rdfs:range xsd:string`. Giving it a `time:ProperInterval` IRI as a value would make it
    an object property as well, which OWL 2 DL forbids.
  - No class lists `temporal_interval_qualifier` among its slots. The only association that uses
    either slot is `exposure event to outcome association`, and it uses
    `temporal_context_qualifier`. Biolink's SHACL shape for `Association` is closed and doesn't
    list `temporal_interval_qualifier`. pyshacl 0.40.1 rejects a synthetic `Association` carrying
    it (a `ClosedConstraintComponent` violation), whether the value is an interval IRI or a
    string.

  *Why it matters*: the Ontology Rigor criterion (20%) asks for Biolink consistency, and our
  ideas assumed these slots could carry OWL-Time intervals. They can't as published. Options
  are to propose a Biolink change (a class range for `temporal_interval_qualifier`, aligned to
  `time:ProperInterval`, and adding it to association slots), or to use our own object property
  mapped to the Biolink slot and say why in the write-up. An upstream proposal would also
  speak to Feasibility & Integration (15%).
- **OWL-Time** <https://www.w3.org/TR/owl-time/>, namespace `http://www.w3.org/2006/time#`.
  Named in the submission requirements as an acceptable vocabulary. `time:Instant`,
  `time:ProperInterval`, `time:hasBeginning`, `time:hasEnd`, `time:inXSDDateTimeStamp`, and the
  thirteen Allen relations (`time:intervalBefore`, `time:intervalMeets`, `time:intervalDuring`,
  ...). *Why it matters*: gives interval algebra as OWL object properties, so ordering
  constraints can be stated as axioms.
- **Allen's interval algebra**: J. F. Allen, "Maintaining Knowledge about Temporal Intervals",
  Communications of the ACM 26(11), 1983, <https://doi.org/10.1145/182.358434>. The thirteen
  relations and their composition table; the basis for OWL-Time's interval relations and for
  any "is this sequence of events consistent?" check.
- **Relations Ontology (RO)** <https://obofoundry.org/ontology/ro>, browse at
  <https://www.ebi.ac.uk/ols4/ontologies/ro>. Temporal relations: `BFO:0000063` precedes,
  `BFO:0000062` preceded by, `RO:0002090` immediately precedes, `RO:0002087` immediately
  preceded by, `RO:0002092` happens during, `RO:0002081` before or simultaneous with,
  `RO:0002082` simultaneous with. Causal relations: `RO:0002411` causally upstream of,
  `RO:0002418` causally upstream of or within, and the direct regulation relations used by
  GO-CAM. *Why it matters*: OBO-native vocabulary for both ordering and causality, already in
  Ubergraph and Biolink mappings.
- **Basic Formal Ontology (BFO)** <https://basic-formal-ontology.org/>. Distinguishes
  continuants (patients, drugs) from occurrents (processes, temporal regions) and provides
  `BFO:0000008` temporal region, `BFO:0000015` process. *Why it matters*: most OBO ontologies
  the rubric points at are BFO-based, so a temporal model that respects the continuant /
  occurrent split integrates more cleanly.
- **OBO ontologies likely to be reused**: MONDO (disease), HP (phenotypes), CHEBI (chemicals),
  NCIT (cancer staging, procedures), OAE Ontology of Adverse Events, DRON Drug Ontology, OGMS
  Ontology for General Medical Science (diagnosis, disease course), IDO Infectious Disease
  Ontology. Browse all at <https://obofoundry.org/>.
- **NLM vocabularies**: SNOMED CT, LOINC, RxNorm, and MeSH via UMLS
  <https://www.nlm.nih.gov/research/umls/>. The rubric says "NLM or OBO". RxNorm is the
  natural drug vocabulary for care pathways and pharmacovigilance.
- **W3C PROV-O** <https://www.w3.org/TR/prov-o/>. `prov:generatedAtTime`,
  `prov:invalidatedAtTime`, `prov:wasRevisionOf`, `prov:wasDerivedFrom`. *Why it matters*: the
  "evidence evolution" and "no fact asserted before its supporting evidence holds" language in
  the rubric is provenance with timestamps; PROV-O is the standard for it.
- **RDF 1.2 / RDF-star** <https://www.w3.org/TR/rdf12-concepts/>. Statements about statements
  without reification blank nodes. *Why it matters*: one of the three mainstream ways to attach
  a validity interval to a triple (the others being named graphs and association nodes as in
  Biolink and Wikidata).
- **Temporal RDF**: C. Gutierrez, C. Hurtado, A. Vaisman, "Introducing Time into RDF", IEEE
  TKDE 19(2), 2007, <https://doi.org/10.1109/TKDE.2007.34>. The formal treatment of
  validity-time-labelled triples and temporal entailment.
- **DatalogMTL** (metric temporal logic over Datalog): S. Brandt et al., "Ontology-Based Data
  Access with a Horn Fragment of Metric Temporal Logic", AAAI 2017, and follow-ups from the
  Oxford KRR group. *Why it matters*: a rule language with temporal operators, an alternative to
  OWL for "time-respecting inference" if DL turns out too weak. To read.

## Clinical and public-health data models with time built in

- **OMOP Common Data Model** (OHDSI) <https://ohdsi.github.io/CommonDataModel/>. Every clinical
  event table has start and end dates; eras (drug era, condition era) are derived intervals.
  *Why it matters*: the most widely deployed example of interval-stamped clinical facts; a
  temporal KG that can round-trip OMOP is immediately relevant to real workflows.
- **HL7 FHIR** <https://hl7.org/fhir/>. `Period`, `effectivePeriod`, `MedicationStatement`,
  `Condition.onset[x]` / `abatement[x]`. *Why it matters*: the interchange format clinical
  systems actually emit; FHIR RDF exists.
- **Synthea** <https://synthetichealth.github.io/synthea/>. Open-source synthetic patient
  generator (MITRE) producing FHIR bundles and CSVs with full longitudinal histories, no PHI.
  *Why it matters*: a second source of synthetic longitudinal data to complement the
  clinical-notes generator above, and one judges will recognize.
- **FDA FAERS** <https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html> and
  **openFDA** <https://open.fda.gov/>. Adverse-event reports with event dates and drug start
  and end dates; drug label histories via DailyMed <https://dailymed.nlm.nih.gov/>. *Why it
  matters*: public pharmacovigilance data with the timestamps needed for exposure-window and
  label-change questions. Download targets: `data/faers/`, `data/dailymed/`.
- **ClinicalTrials.gov** <https://clinicaltrials.gov/> with its record version history. *Why it
  matters*: evidence that changes over time, with timestamps.
- **Infectious-disease surveillance**: Nextstrain <https://nextstrain.org/> (dated phylogenies
  and variant frequencies), outbreak.info <https://outbreak.info/>, CDC data at
  <https://data.cdc.gov/>. *Why it matters*: variant dominance by week and region, intervention
  availability dates, incubation and serial-interval estimates.
- **Restricted but relevant**: MIMIC-IV <https://physionet.org/content/mimiciv/> requires
  credentialing and a data-use agreement; de-identified, but still must never be committed here.

## Clinical temporal ontologies and corpora

- **CNTRO** (Clinical Narrative Temporal Relation Ontology): C. Tao et al., "CNTRO: A Semantic
  Web Ontology for Temporal Relation Inferencing in Clinical Narratives", AMIA Annual Symposium
  2010, <https://pubmed.ncbi.nlm.nih.gov/21347086/>; and "CNTRO 2.0: A Harmonized Semantic Web
  Ontology for Temporal Relation Inferencing in Clinical Narratives", AMIA Joint Summits 2011,
  <https://pubmed.ncbi.nlm.nih.gov/22211182/>. An OWL ontology for temporal relations in
  clinical narratives, with inference. *Why it matters*: prior art that is very close to what
  the rubric asks for; we should know what it did and why it did not become standard.
- **CNTRO applied to adverse events**: K. K. Clark et al., "Application of a temporal reasoning
  framework tool in analysis of medical device adverse events", AMIA Annual Symposium 2011,
  <https://pubmed.ncbi.nlm.nih.gov/22195199/>; and K. Clark et al., "A use case study on late
  stent thrombosis for ontology-based temporal reasoning and analysis", Journal of Biomedical
  Semantics 2014, <https://pubmed.ncbi.nlm.nih.gov/25540680/>. *Why it matters*: ontology-based
  temporal reasoning over adverse-event reports is one of the three NIH domains; these are the
  closest published precedents for the pharmacovigilance competency questions.
- **TEO** (Time Event Ontology): F. Li et al., "Time event ontology (TEO): to support semantic
  representation and reasoning of complex temporal relations of clinical events", JAMIA 27(7),
  2020, <https://doi.org/10.1093/jamia/ocaa058>. Successor to CNTRO with reasoning support.
- **i2b2 2012 Temporal Relations Challenge**: W. Sun, A. Rumshisky, O. Uzuner, JAMIA 20(5),
  2013, <https://doi.org/10.1136/amiajnl-2013-001628>. Annotated clinical notes with events,
  time expressions, and TLINKs. *Why it matters*: an established benchmark shape for "extract
  the timeline from a note", relevant if synthetic notes are the input.
- **THYME corpus**: W. F. Styler IV et al., "Temporal Annotation in the Clinical Domain", TACL 2,
  2014, <https://doi.org/10.1162/tacl_a_00172>. Clinical TimeML.

## Temporal knowledge-graph embeddings and reasoning (to read)

The rubric names "temporal embeddings" explicitly, so an entry should at least position itself
relative to this literature even if the core is symbolic.

- Survey: B. Cai et al., "Temporal Knowledge Graph Completion: A Survey", 2022,
  <https://arxiv.org/abs/2201.08236>. Covers TTransE, TA-DistMult, DE-SimplE, TNTComplEx,
  TeRo, and the standard benchmarks ICEWS14, ICEWS05-15, GDELT, YAGO11k, Wikidata12k.
- Explainable temporal rule learning: Y. Liu et al., "TLogic: Temporal Logical Rules for
  Explainable Link Forecasting on Temporal Knowledge Graphs", AAAI 2022,
  <https://arxiv.org/abs/2112.08025>. *Why it matters*: rule-based forecasting is a bridge
  between the embedding literature and the "machine-verifiable" language in the rubric.
- Note: all of the standard tKG benchmarks are political-event or encyclopedic data, not
  biomedical. A biomedical temporal benchmark would itself be a contribution, and Phase 2 says
  effectiveness is measured on "shared benchmark tasks", so watch the Q&A forum for what NIH
  intends to share.

## Wikidata as a worked example of time qualifiers

- Help pages: <https://www.wikidata.org/wiki/Help:Qualifiers>,
  <https://www.wikidata.org/wiki/Help:Ranking>.
- Properties: `P580` start time, `P582` end time, `P585` point in time, `P1082` population,
  `P6` head of government, `P459` determination method.
- Example: Raleigh, North Carolina <https://www.wikidata.org/wiki/Q41087>. Its population
  statements each carry `P585` and `P459` (census vs estimate), with the 2020 census value
  ranked *preferred*; its head-of-government statements carry `P580` start times with the
  current mayor ranked *preferred*.
- Query service: <https://query.wikidata.org/>.
- See [ideas/wikidata-qualifiers.md](../ideas/wikidata-qualifiers.md).

## Methodology

- Competency questions: M. Grüninger and M. S. Fox, "Methodology for the Design and Evaluation
  of Ontologies", IJCAI-95 Workshop on Basic Ontological Issues in Knowledge Sharing, 1995.
  The origin of the term as used in [competency-questions/](../competency-questions/README.md).
- Ontology QA and reasoning tooling: ROBOT <http://robot.obolibrary.org/>, Ontology Development
  Kit <https://github.com/INCATools/ontology-development-kit>. ROBOT `reason` and `report` are
  the obvious way to produce the "logical inconsistencies / unsatisfiable classes" number.

## Prior challenges worth reading for how winners were judged

- NIH challenge listing: <https://www.nih.gov/challenges>. ODSS has run several data-science
  prize competitions; reading their winner announcements shows what "clearly and completely
  presented" tends to mean in practice.
- Challenge.gov: <https://www.challenge.gov/>.
