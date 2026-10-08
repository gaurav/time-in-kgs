# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.25",
#     "duckdb>=1.3",
#     "polars>=1.0",
#     "pyarrow>=17",
#     "altair>=5.4",
# ]
# ///
"""First look at openFDA Animal & Veterinary adverse events and ICDC clinical records.

Run with:  uvx marimo edit --sandbox ideas/veterinary-adverse-events/analysis.py
Export:    uvx marimo export html --sandbox ideas/veterinary-adverse-events/analysis.py -o out.html

Needs the data downloaded by download_openfda_animal.py and download_icdc.py (see README.md).
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Veterinary adverse events as temporal test data

        A first look at two public, PHI-free sources against the
        [competency questions](../../competency-questions/README.md): openFDA's
        **Animal & Veterinary adverse-event reports** (2025 Q1 to 2026 Q2) and the
        **Integrated Canine Data Commons** (ICDC) clinical-trial records. Each section names the
        competency question it speaks to and what the data can and cannot support.
        """
    )
    return


@app.cell
def _():
    import json
    from pathlib import Path

    import altair as alt
    import duckdb
    import marimo as mo
    import polars as pl

    REPO = mo.notebook_dir().parent.parent
    OPENFDA = REPO / "data" / "openfda" / "animalandveterinary" / "event"
    ICDC = REPO / "data" / "icdc"

    # Chart palette: the validated default from the dataviz skill (slots 1 and 2, blue ramp).
    BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#898781"
    BLUE_RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
    return BLUE, BLUE_RAMP, GRAY, ICDC, OPENFDA, ORANGE, Path, alt, duckdb, json, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 1. Load

        openFDA ships one JSON file per quarter, each a `results` array of nested report objects.
        DuckDB reads them directly. Two quirks: a handful of records carry a date as a one- or
        two-element JSON array instead of a string, so DuckDB types those columns as `JSON`; and
        dates are `YYYYMMDD` strings, occasionally partial. The `jstr` and `ymd` macros below
        normalise both. The nested arrays are flattened into three tables: `reports`, `drugs`
        (one row per drug per report) and `reactions` (one row per VeDDRA term per report).
        """
    )
    return


@app.cell
def _(OPENFDA, duckdb, json):
    snapshot = json.loads((OPENFDA / "manifest-snapshot.json").read_text())
    con = duckdb.connect()
    con.execute(
        f"""
        CREATE VIEW raw AS
            SELECT unnest(results) AS r
            FROM read_json('{OPENFDA}/*/*.json', maximum_object_size=400000000);
        CREATE MACRO jstr(x) AS CASE WHEN json_type(x) = 'ARRAY'
            THEN json_extract_string(x, '$[0]') ELSE json_extract_string(x, '$') END;
        CREATE MACRO ymd(s) AS CASE WHEN length(s) = 8
            THEN try_strptime(s, '%Y%m%d')::DATE END;

        CREATE TABLE reports AS SELECT
            r.unique_aer_id_number AS id,
            ymd(jstr(r.original_receive_date)) AS receive_date,
            ymd(jstr(r.onset_date)) AS onset_date,
            coalesce(nullif(r.animal.species, ''), '(not recorded)') AS species,
            r.serious_ae = 'true' AS serious,
            r.type_of_information AS type_of_information,
            len(r.drug) AS n_drugs,
            len(r.reaction) AS n_reactions
        FROM raw;

        CREATE TABLE drugs AS SELECT
            r.unique_aer_id_number AS id,
            d.brand_name,
            d.atc_vet_code,
            lower(array_to_string(list_transform(d.active_ingredients, a -> a.name), ' | ')) AS ingredients,
            ymd(d.first_exposure_date) AS first_exposure,
            ymd(d.last_exposure_date) AS last_exposure,
            d.previous_exposure_to_drug AS previous_exposure,
            d.ae_abated_after_stopping_drug AS abated_after_stopping,
            d.ae_reappeared_after_resuming_drug AS reappeared_after_resuming
        FROM (SELECT r, unnest(r.drug) AS d FROM raw);

        CREATE TABLE reactions AS SELECT
            r.unique_aer_id_number AS id,
            x.veddra_term_code AS term_code,
            x.veddra_term_name AS term,
            x.veddra_version AS veddra_version
        FROM (SELECT r, unnest(r.reaction) AS x FROM raw);
        """
    )

    def sql(query: str):
        """Run a query and return a polars DataFrame."""
        return con.execute(query).pl()

    counts = sql("SELECT (SELECT count(*) FROM reports) AS reports, (SELECT count(*) FROM drugs) AS drug_rows, (SELECT count(*) FROM reactions) AS reaction_rows")
    counts
    return con, counts, snapshot, sql


@app.cell(hide_code=True)
def _(counts, mo, snapshot):
    mo.md(
        f"""
        Loaded **{counts["reports"][0]:,} reports** ({counts["drug_rows"][0]:,} drug rows,
        {counts["reaction_rows"][0]:,} reaction rows) from the openFDA export dated
        **{snapshot["export_date"]}**, covering quarters
        {", ".join(p["quarter"] for p in snapshot["partitions"])}.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 2. Overview

        Reports are indexed by the date FDA received them. Dogs dominate; the "(not recorded)"
        species are almost all product-defect reports with no animal. VeDDRA (the Veterinary
        Dictionary for Drug Related Affairs) codes the reactions; ATCvet codes the products.
        """
    )
    return


@app.cell
def _(BLUE, alt, sql):
    per_quarter = sql(
        """
        SELECT strftime(receive_date, '%Y') || ' Q' || quarter(receive_date) AS quarter, count(*) AS reports
        FROM reports WHERE receive_date IS NOT NULL GROUP BY 1 ORDER BY 1
        """
    )
    alt.Chart(per_quarter, title="Reports received per quarter").mark_bar(
        color=BLUE, cornerRadiusTopLeft=4, cornerRadiusTopRight=4
    ).encode(
        x=alt.X("quarter:N", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("reports:Q", title="Reports"),
        tooltip=["quarter", alt.Tooltip("reports", format=",")],
    ).properties(width=480, height=220)
    return


@app.cell
def _(mo, sql):
    species = sql(
        """
        SELECT species, count(*) AS reports,
               round(100.0 * avg(CASE WHEN serious THEN 1 ELSE 0 END), 1) AS pct_serious
        FROM reports GROUP BY 1 ORDER BY 2 DESC LIMIT 8
        """
    )
    top_terms = sql(
        "SELECT term, count(*) AS reports FROM reactions GROUP BY 1 ORDER BY 2 DESC LIMIT 12"
    )
    top_atc = sql(
        """
        SELECT substr(atc_vet_code, 1, 5) AS atcvet_group, count(*) AS drug_rows
        FROM drugs WHERE atc_vet_code IS NOT NULL AND atc_vet_code <> 'UNKNOWN'
        GROUP BY 1 ORDER BY 2 DESC LIMIT 10
        """
    )
    mo.hstack([species, top_terms, top_atc], justify="start", gap=2, wrap=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 3. Timestamp quality

        Every report has a receive date. Most have an onset date, and most drug rows have a first
        exposure date; the last exposure date is missing for about a quarter of them, which
        matters for any "was the animal still exposed at onset" question. A **negative lag**
        (onset after the receive date) cannot occur in an original report, so those records
        show that the snapshot includes later amendments (see section 7).
        """
    )
    return


@app.cell
def _(pl, sql):
    completeness = sql(
        """
        SELECT 'reports' AS "table", 'receive_date' AS field, count(receive_date) AS present, count(*) AS total FROM reports
        UNION ALL SELECT 'reports', 'onset_date', count(onset_date), count(*) FROM reports
        UNION ALL SELECT 'drugs', 'first_exposure', count(first_exposure), count(*) FROM drugs
        UNION ALL SELECT 'drugs', 'last_exposure', count(last_exposure), count(*) FROM drugs
        UNION ALL SELECT 'reports', 'onset after receive (impossible in an original report)',
            count(*) FILTER (WHERE onset_date > receive_date), count(*) FROM reports
        """
    ).with_columns((100 * pl.col("present") / pl.col("total")).round(1).alias("pct"))
    completeness
    return


@app.cell
def _(BLUE, alt, mo, sql):
    lag_quantiles = sql(
        """
        SELECT quantile_cont(lag, 0.25) AS q25, quantile_cont(lag, 0.5) AS median,
               quantile_cont(lag, 0.75) AS q75, quantile_cont(lag, 0.95) AS q95,
               count(*) FILTER (WHERE lag > 365) AS over_a_year, count(*) FILTER (WHERE lag < 0) AS negative
        FROM (SELECT date_diff('day', onset_date, receive_date) AS lag FROM reports WHERE onset_date IS NOT NULL)
        """
    )
    lag_hist = sql(
        """
        SELECT 7 * floor(lag / 7) AS week_start, count(*) AS reports
        FROM (SELECT date_diff('day', onset_date, receive_date) AS lag FROM reports WHERE onset_date IS NOT NULL)
        WHERE lag BETWEEN 0 AND 364 GROUP BY 1 ORDER BY 1
        """
    )
    lag_chart = alt.Chart(lag_hist, title="Days from onset to FDA receipt (first year only)").mark_bar(
        color=BLUE, cornerRadiusTopLeft=4, cornerRadiusTopRight=4
    ).encode(
        x=alt.X("week_start:Q", title="Days (7-day bins)"),
        y=alt.Y("reports:Q", title="Reports"),
        tooltip=[alt.Tooltip("week_start", title="From day"), alt.Tooltip("reports", format=",")],
    ).properties(width=480, height=220)
    mo.vstack([lag_quantiles, lag_chart])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 4. CQ-PV-M01: co-administered drugs in the windows before onset

        > For adverse-event report R, which drugs were co-administered during the 30 days before
        > the event onset, and which were started within 7 days of it?

        The report below is chosen deterministically: the one with the most drugs that have both
        an exposure date and an onset date. A drug counts as *active in the 30 days before
        onset* if its first exposure is on or before onset and its last exposure (or an open end)
        is within 30 days before onset; it counts as *started within 7 days* if the first
        exposure falls in the week ending at onset. Below it, the same classification across all
        drug rows with both dates.
        """
    )
    return


@app.cell
def _(mo, sql):
    m01_id = sql(
        """
        SELECT d.id FROM drugs d JOIN reports r USING (id)
        WHERE r.onset_date IS NOT NULL AND d.first_exposure IS NOT NULL
        GROUP BY d.id ORDER BY count(*) DESC, d.id LIMIT 1
        """
    )["id"][0]
    m01_windows = f"""
        SELECT d.id, r.onset_date, d.brand_name, d.ingredients, d.first_exposure, d.last_exposure,
            d.first_exposure <= r.onset_date
                AND coalesce(d.last_exposure, r.onset_date) >= r.onset_date - INTERVAL 30 DAY AS active_30d_before,
            d.first_exposure BETWEEN r.onset_date - INTERVAL 7 DAY AND r.onset_date AS started_within_7d,
            d.first_exposure > r.onset_date AS started_after_onset
        FROM drugs d JOIN reports r USING (id)
        WHERE r.onset_date IS NOT NULL AND d.first_exposure IS NOT NULL
    """
    m01_sample = sql(f"SELECT * FROM ({m01_windows}) WHERE id = '{m01_id}' ORDER BY first_exposure")
    m01_cohort = sql(
        f"""
        SELECT active_30d_before, started_within_7d, started_after_onset, count(*) AS drug_rows
        FROM ({m01_windows}) GROUP BY 1, 2, 3 ORDER BY 4 DESC
        """
    )
    mo.vstack([mo.md(f"Sample report `{m01_id}`:"), m01_sample, mo.md("All drug rows with both dates:"), m01_cohort])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 5. CQ-PV-M04: does exposure precede the event?

        > Across a set of reports for drug D and event A, in which does the exposure precede the
        > event, in which does the event precede the exposure, and does the ontology treat the
        > second kind as evidence against causality rather than for it?

        D = the isoxazoline flea-and-tick drugs (afoxolaner, fluralaner, sarolaner, lotilaner),
        matched on active ingredient because combination products carry other ATCvet codes.
        A = any VeDDRA seizure or convulsion term. "Onset before exposure" is usually not an
        impossibility: the exposure recorded is a later dose, and `previous_exposure_to_drug`
        says whether the animal had the product before. A temporal model has to hold both the
        recorded dose interval and the possibility of earlier, unrecorded doses.
        """
    )
    return


@app.cell
def _(mo, sql):
    ISOXAZOLINE = "(afoxolaner|fluralaner|sarolaner|lotilaner)"
    SEIZURE = "(seizure|convuls)"
    m04_pairs = f"""
        SELECT r.id, r.onset_date, d.first_exposure, d.previous_exposure
        FROM reports r
        JOIN drugs d ON d.id = r.id AND regexp_matches(d.ingredients, '{ISOXAZOLINE}')
        WHERE EXISTS (SELECT 1 FROM reactions x WHERE x.id = r.id AND regexp_matches(lower(x.term), '{SEIZURE}'))
    """
    m04_order = sql(
        f"""
        SELECT CASE WHEN onset_date IS NULL OR first_exposure IS NULL THEN 'unknown'
                    WHEN first_exposure <= onset_date THEN 'exposure before or at onset'
                    ELSE 'onset before recorded exposure' END AS ordering,
               coalesce(previous_exposure, 'not stated') AS previous_exposure,
               count(DISTINCT id) AS reports
        FROM ({m04_pairs}) GROUP BY 1, 2 ORDER BY 1, 2
        """
    )
    m04_total = sql(f"SELECT count(DISTINCT id) AS reports FROM ({m04_pairs})")["reports"][0]
    mo.vstack([mo.md(f"**{m04_total:,} reports** pair an isoxazoline exposure with a seizure term."), m04_order])
    return ISOXAZOLINE, SEIZURE


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 6. CQ-PV-H02: a disproportionality signal "as of T", and what leakage looks like

        > Using only reports received on or before date T, what is the disproportionality signal
        > for drug D and event A, how does it evolve as T advances?

        The proportional reporting ratio (PRR) for D and A at time T compares the share of
        D-reports mentioning A with the share of non-D reports mentioning A, over reports known
        at T. The honest series uses the **receive date**: at T, FDA holds exactly the reports
        received by T. The leaky series uses the **onset date**: it counts, at T, every report
        whose event had happened by T, including reports FDA only received months later. The
        gap between the two is what the Reasoning Correctness criterion calls temporal leakage.

        Both series start from an empty set in 2025-01, so the first months are small-sample.
        Relating the signal to regulatory action needs older years: FDA's
        [safety communication on neurologic events with isoxazolines](https://www.fda.gov/animal-veterinary/cvm-updates/animal-drug-safety-communication-fda-alerts-pet-owners-and-veterinarians-about-potential-neurologic)
        is dated 2018-09-20, and the downloader takes `--years` to fetch those years.
        """
    )
    return


@app.cell
def _(BLUE, ISOXAZOLINE, ORANGE, SEIZURE, alt, pl, sql):
    h02_flags = f"""
        SELECT r.id, r.receive_date, r.onset_date,
            EXISTS (SELECT 1 FROM drugs d WHERE d.id = r.id AND regexp_matches(d.ingredients, '{ISOXAZOLINE}')) AS is_d,
            EXISTS (SELECT 1 FROM reactions x WHERE x.id = r.id AND regexp_matches(lower(x.term), '{SEIZURE}')) AS is_a
        FROM reports r
    """

    def prr_series(date_column: str, label: str):
        return sql(
            f"""
            WITH flags AS ({h02_flags}),
            months AS (SELECT unnest(generate_series(DATE '2025-01-31', DATE '2026-06-30', INTERVAL 1 MONTH))::DATE AS t)
            SELECT t, '{label}' AS series,
                count(*) FILTER (WHERE is_d AND is_a) AS a,
                count(*) FILTER (WHERE is_d AND NOT is_a) AS b,
                count(*) FILTER (WHERE NOT is_d AND is_a) AS c,
                count(*) FILTER (WHERE NOT is_d AND NOT is_a) AS d
            FROM months JOIN flags ON flags.{date_column} <= months.t
            GROUP BY t ORDER BY t
            """
        ).with_columns(
            ((pl.col("a") / (pl.col("a") + pl.col("b"))) / (pl.col("c") / (pl.col("c") + pl.col("d")))).alias("prr")
        )

    h02 = pl.concat([
        prr_series("receive_date", "as of receive date (no leakage)"),
        prr_series("onset_date", "by onset date (leaks later reports)"),
    ])
    h02_lines = alt.Chart(h02, title="PRR, isoxazolines x seizure terms, cumulative to month end").mark_line(
        strokeWidth=2, point=alt.OverlayMarkDef(size=40)
    ).encode(
        x=alt.X("t:T", title=None),
        y=alt.Y("prr:Q", title="Proportional reporting ratio"),
        color=alt.Color("series:N", title=None, scale=alt.Scale(range=[BLUE, ORANGE]), legend=alt.Legend(orient="bottom")),
        tooltip=[alt.Tooltip("t:T", title="As of"), "series", alt.Tooltip("prr:Q", format=".2f"), alt.Tooltip("a", title="D and A reports")],
    ).properties(width=560, height=260)
    h02_lines
    return (h02,)


@app.cell
def _(h02, pl):
    import datetime as dt

    h02.filter(pl.col("t").is_in([dt.date(2025, 3, 31), dt.date(2025, 6, 30), dt.date(2025, 12, 31), dt.date(2026, 6, 30)])).sort("t", "series")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 7. Snapshot limits (CQ-XX-H02)

        > For an answer computed "as of" time T, can the system produce a derivation showing
        > that every assertion used has transaction time at or before T?

        Only approximately, from this source. openFDA publishes FDA's *current* view of each
        report: there is one record per `unique_aer_id_number` (no duplicates across the six
        quarterly files), no version history, and no field saying when a record was last
        amended. The reports whose onset date is after their receive date prove that amendments
        happen and overwrite the original. So "received by T" is reconstructible from the
        receive date, but "the content FDA held at T" is not: a report received in 2025-03 and
        amended in 2026-01 appears here only in its amended form. A derivation can therefore
        certify the *report set* at T, not the *report content* at T. The honest statement of
        transaction time for every assertion in this snapshot is the export date in
        `manifest-snapshot.json`.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 8. ICDC quick look (care-pathway analogue)

        The ICDC GraphQL API exposes trial records per dog. On 2026-10-07 the treatment nodes
        (`agent_administration`, `follow_up`, `off_treatment`, `prior_therapy`) were empty for
        every study; dated clinical records exist for the PRECINCT trials (visits and adverse
        events) and COTC007B (cycles). For the osteosarcoma standard-of-care trials (COTC021,
        COTC022) the dated pathway (surgery, carboplatin doses, off-study date, survival) lives
        in study-level spreadsheets instead, which the downloader also fetches.
        """
    )
    return


@app.cell
def _(ICDC, json, pl):
    import re
    from datetime import date

    SENTINEL = "3501-08-15"

    def parse_icdc_date(value):
        """ICDC dates arrive as 2014-03-06 or 11/21/2018, with '' and a 3501 sentinel for missing."""
        if not value or value.startswith("3501"):
            return None
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return date.fromisoformat(value)
        if m := re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", value):
            return date(int(m[3]), int(m[1]), int(m[2]))
        return None

    def date_kind(value):
        if value is None:
            return "null"
        if value == "":
            return "empty"
        if value.startswith(SENTINEL[:4]):
            return "sentinel 3501"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return "ISO"
        if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", value):
            return "M/D/YYYY"
        return "other"

    icdc = {p.stem: json.loads(p.read_text()) for p in ICDC.glob("*.json") if p.stem != "fetch-info"}
    icdc_info = json.loads((ICDC / "fetch-info.json").read_text())

    def study_of(record):
        case = record.get("case") or (record.get("enrollment") or {}).get("case") or (record.get("visit") or {}).get("case")
        if case:
            return case["case_id"].split("-")[0]
        return (record.get("study") or {}).get("clinical_study_designation", "?")

    node_rows = [
        {"node": node, "study": study_of(rec)}
        for node, recs in icdc.items() if node != "study"
        for rec in recs
    ]
    icdc_counts = (
        pl.DataFrame(node_rows).group_by("study", "node").len().pivot("node", index="study", values="len").fill_null(0).sort("study")
    )
    date_fields = {
        "cycle": ["date_of_cycle_start", "date_of_cycle_end"], "visit": ["visit_date"],
        "adverse_event": ["date_of_onset", "date_of_resolution"], "diagnosis": ["date_of_diagnosis"],
        "enrollment": ["date_of_registration"], "demographic": ["date_of_birth"],
    }
    icdc_dates = pl.DataFrame([
        {"node": node, "field": field, "kind": date_kind(rec.get(field))}
        for node, fields in date_fields.items() for field in fields for rec in icdc[node]
    ]).group_by("node", "field", "kind").len().pivot("kind", index=["node", "field"], values="len").fill_null(0).sort("node", "field")
    return date, icdc, icdc_counts, icdc_dates, icdc_info, parse_icdc_date, re


@app.cell
def _(icdc_counts, icdc_dates, icdc_info, mo):
    mo.vstack([
        mo.md(f"Fetched {icdc_info['fetched_at'][:10]}, schema {icdc_info['schema_version']}: {icdc_info['number_of_studies']} studies, {icdc_info['number_of_cases']} cases. Records per node and study:"),
        icdc_counts,
        mo.md("Date formats per field (an audit a temporal model has to pass before any ordering axiom applies):"),
        icdc_dates,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### One case timeline

        A PRECINCT02 lymphoma case with many visits and adverse events (chosen as the one with
        the most of each), the kind of record behind CQ-CP-E03 (days between two pathway
        events), CQ-CP-M03 (which conditions started and later resolved, with their intervals)
        and CQ-CP-M04 (did events happen in the expected order). Adverse events with a
        resolution date are drawn as intervals, those without as points; grade is the
        VCOG-CTCAE grade. Case IDs are the public identifiers ICDC itself displays.
        """
    )
    return


@app.cell
def _(BLUE_RAMP, GRAY, alt, icdc, parse_icdc_date, pl):
    from collections import Counter

    tl_visits = Counter(v["case"]["case_id"] for v in icdc["visit"] if v.get("case"))
    tl_aes = Counter(a["case"]["case_id"] for a in icdc["adverse_event"] if a.get("case"))
    tl_case = max((c for c in tl_visits if c.startswith("PRECINCT02")), key=lambda c: tl_visits[c] + tl_aes[c])

    tl_visit_df = pl.DataFrame({
        "date": [parse_icdc_date(v["visit_date"]) for v in icdc["visit"] if v.get("case") and v["case"]["case_id"] == tl_case],
        "row": "visit",
    })
    tl_ae_df = pl.DataFrame([
        {
            "term": a["adverse_event_term"],
            "grade": a["adverse_event_grade"],
            "onset": parse_icdc_date(a["date_of_onset"]),
            "resolution": parse_icdc_date(a["date_of_resolution"]),
        }
        for a in icdc["adverse_event"] if a.get("case") and a["case"]["case_id"] == tl_case
    ]).filter(pl.col("onset").is_not_null())
    tl_dx = [parse_icdc_date(d["date_of_diagnosis"]) for d in icdc["diagnosis"] if d.get("case") and d["case"]["case_id"] == tl_case]

    grade_scale = alt.Scale(domain=["1", "2", "3", "4", "5"], range=BLUE_RAMP)
    tl_intervals = alt.Chart(tl_ae_df.filter(pl.col("resolution").is_not_null())).mark_bar(height=10, cornerRadius=4).encode(
        x=alt.X("onset:T", title=None), x2="resolution:T", y=alt.Y("term:N", title=None, sort=None),
        color=alt.Color("grade:N", title="Grade", scale=grade_scale),
        tooltip=["term", "grade", "onset:T", "resolution:T"],
    )
    tl_points = alt.Chart(tl_ae_df.filter(pl.col("resolution").is_null())).mark_point(size=70, filled=True).encode(
        x="onset:T", y=alt.Y("term:N", sort=None), color=alt.Color("grade:N", scale=grade_scale),
        tooltip=["term", "grade", "onset:T"],
    )
    tl_ticks = alt.Chart(tl_visit_df).mark_tick(color=GRAY, thickness=2, size=14).encode(
        x="date:T", y=alt.Y("row:N", title=None), tooltip=["date:T"]
    )
    tl_rule = alt.Chart(pl.DataFrame({"date": tl_dx, "what": "diagnosis"})).mark_rule(color=GRAY, strokeDash=[4, 3]).encode(x="date:T", tooltip=["what", "date:T"])
    (tl_intervals + tl_points + tl_ticks + tl_rule).properties(
        width=600, height=320, title=f"{tl_case}: visits (ticks), adverse events (by grade), diagnosis (dashed)"
    ).resolve_scale(y="shared")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 9. Ontology mapping notes (Ontology Rigor, 20%)

        | Field | Vocabulary in the data | OBO or NLM? | Mapping route |
        |---|---|---|---|
        | `animal.species` | free text (Dog, Cat, Horse...) | map to **NCBITaxon** (OBO) | small lookup table |
        | `animal.breed.breed_component` | free text | **Vertebrate Breed Ontology** (VBO, OBO) | string match, then curate |
        | `reaction.veddra_term_name` / code | **VeDDRA** v21 | no (EMA-maintained, not OBO) | keep VeDDRA codes; map common terms to **HP**/**OAE** where a counterpart exists |
        | `drug.atc_vet_code` | **ATCvet** | no (WHO) | keep; map ingredients to **ChEBI** (OBO) or RxNorm/UNII (NLM) |
        | `drug.active_ingredients.name` | free text with dose | ChEBI / UNII | parse, then map |
        | ICDC `adverse_event_term` | **VCOG-CTCAE** style terms | no | map to HP/OAE as for VeDDRA |
        | ICDC `disease_term` | free text (B Cell Lymphoma...) | **MONDO** or NCIT (OBO/NLM) | lookup |
        | Dates and intervals | strings | **OWL-Time** | `time:Instant` with `time:inXSDDate`; exposure and AE intervals as `time:ProperInterval` |

        VeDDRA and ATCvet are the gap: the rubric rewards NLM/OBO reuse, and neither is either.
        The defensible position is to keep them as the source coding (they are the regulatory
        standard for this data) and add OBO cross-references for the terms a competency question
        touches.
        """
    )
    return


if __name__ == "__main__":
    app.run()
