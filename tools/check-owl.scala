//> using scala 3.6.4
//> using dep org.apache.jena:jena-arq:5.2.0
//> using dep net.sourceforge.owlapi:owlapi-distribution:4.5.29
//> using dep net.sourceforge.owlapi:org.semanticweb.hermit:1.4.5.456
//> using dep org.slf4j:slf4j-nop:2.0.16

// Checks an RDF/XML ontology file four ways and prints what each one says:
//
//   1. Apache Jena RIOT in strict mode, the strictest widely used RDF/XML parser.
//   2. The OWL API restricted to its own RDF/XML parser.
//   3. The OWL API with every parser, as ROBOT and Protege load files. It tries each parser
//      until one succeeds, so a file that fails (2) can still load here through a more lenient
//      fallback; the format it reports shows which parser won.
//   4. HermiT: consistency and unsatisfiable classes, which is also one of the Phase 2
//      evaluation metrics (see AGENTS.md).
//
// Usage: scala-cli run tools/check-owl.scala -- path/to/ontology.owl
// Exits non-zero if any check reports an error.

import java.io.File
import scala.jdk.CollectionConverters.*

import org.apache.jena.riot.{Lang, RDFParser}
import org.apache.jena.riot.system.ErrorHandler
import org.apache.jena.sparql.graph.GraphFactory
import org.semanticweb.HermiT.ReasonerFactory
import org.semanticweb.owlapi.apibinding.OWLManager
import org.semanticweb.owlapi.model.AxiomType
import org.semanticweb.owlapi.rdf.rdfxml.parser.RDFXMLParserFactory

@main def checkOwl(path: String): Unit =
  val file = File(path)
  var failed = false

  println(s"== Jena RIOT ${org.apache.jena.Jena.VERSION}, strict RDF/XML")
  val messages = collection.mutable.Buffer[String]()
  def note(level: String)(msg: String, line: Long, col: Long): Unit =
    messages += s"  $level line $line col $col: $msg"
  val handler = new ErrorHandler:
    def warning(msg: String, line: Long, col: Long) = note("WARNING")(msg, line, col)
    def error(msg: String, line: Long, col: Long) = note("ERROR")(msg, line, col)
    def fatal(msg: String, line: Long, col: Long) = note("FATAL")(msg, line, col)
  val graph = GraphFactory.createDefaultGraph()
  try
    RDFParser.source(file.toPath).lang(Lang.RDFXML).strict(true).errorHandler(handler).parse(graph)
    println(s"  parsed: ${graph.size} triples")
  catch case e: Exception =>
    failed = true
    println(s"  FAILED: ${e.getMessage}")
  messages.foreach(println)
  if messages.exists(m => m.contains("ERROR") || m.contains("FATAL")) then failed = true
  if messages.isEmpty then println("  no warnings or errors")

  // OWLOntologyLoaderConfiguration.setStrict(true) is not used: it checks the OWL-to-RDF mapping,
  // not RDF/XML syntax, and rejects even unmodified OWL API output.
  println("== OWL API 4.5.29, RDF/XML parser only")
  val strictManager = OWLManager.createOWLOntologyManager()
  strictManager.setOntologyParsers(Set(RDFXMLParserFactory()).asJava)
  try
    strictManager.loadOntologyFromOntologyDocument(file)
    println("  parsed")
  catch case e: Exception =>
    failed = true
    val cause = e.getMessage.linesIterator.find(_.contains("[line=")).getOrElse(e.getMessage)
    println(s"  FAILED: ${cause.trim.takeWhile(_ != '\t').split("  ").head}")

  println("== OWL API 4.5.29, all parsers (how ROBOT and Protege load files)")
  val manager = OWLManager.createOWLOntologyManager()
  val ontology =
    try Some(manager.loadOntologyFromOntologyDocument(file))
    catch case e: Exception =>
      failed = true
      println(s"  FAILED: ${e.getMessage.linesIterator.take(5).mkString("\n  ")}")
      None

  ontology.foreach { ont =>
    println(s"  loaded as: ${manager.getOntologyFormat(ont).getClass.getSimpleName}")
    println(s"  parsed: ${ont.getLogicalAxiomCount} logical axioms, ${ont.getClassesInSignature.size} classes")
    for t <- AxiomType.AXIOM_TYPES.asScala.toSeq.sortBy(_.getName) do
      val n = ont.getAxiomCount(t)
      if n > 0 && t.isLogical then println(s"    ${t.getName}: $n")

    println("== HermiT")
    val reasoner = ReasonerFactory().createReasoner(ont)
    if reasoner.isConsistent then
      val unsat = reasoner.getUnsatisfiableClasses.getEntitiesMinusBottom.asScala
      println(s"  consistent; ${unsat.size} unsatisfiable classes")
      unsat.foreach(c => println(s"    $c"))
      if unsat.nonEmpty then failed = true
    else
      failed = true
      println("  INCONSISTENT")
    reasoner.dispose()
  }

  if failed then sys.exit(1)
