# Tools

Small JVM scripts run with [Scala CLI](https://scala-cli.virtuslab.org/), which fetches the
Scala compiler and every library declared in a script's `//> using` lines on first run. The only
prerequisites are a JDK (17 or later) and Scala CLI itself (`brew install scala-cli`, or see its
install page).

Scala CLI suits a repo that is mostly notes: it needs no build directory, and each script declares
its own dependencies at the top. The JVM gives us the reference implementations of OWL tooling:
the OWL API (which ROBOT and Protégé are built on), HermiT, and Apache Jena. If the scripts
outgrow single files, put them in a Scala CLI project directory, or convert them to sbt or Maven.

## `check-owl.scala`

```sh
scala-cli run tools/check-owl.scala -- path/to/ontology.owl
```

Parses an RDF/XML ontology with strict Jena, with the OWL API's own RDF/XML parser, and with the
OWL API's full parser chain (how ROBOT and Protégé load files, reporting which parser won). It
then runs HermiT for consistency and unsatisfiable classes. It exits non-zero if any step fails.
Run it on our Phase 1 ontology file before submitting: a file that loads in Protégé can still be
rejected by a strict parser (NIH's own example is one; see
[resources/README.md](../resources/README.md)).
