# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Download clinical records from the Integrated Canine Data Commons (ICDC).

Usage:
    uv run ideas/veterinary-adverse-events/download_icdc.py

Pages through the ICDC GraphQL API (https://caninecommons.cancer.gov/v1/graphql/, open, no
login; the trailing slash matters, without it the server returns 405) and writes one JSON file
per node type to data/icdc/ (gitignored), plus fetch-info.json with the fetch time and schema
version.

The API's treatment nodes (agent_administration, follow_up, off_treatment, prior_therapy) were
empty for every study on 2026-10-07; for some studies that information is published instead as
study-level files ("Supplemental Data File", e.g. "COTC022 SOC Data Set.xlsx", "UBC01 Treatment
and Follow-up.xlsx") and protocols ("Study Protocol"). Those are downloaded to
data/icdc/files/<study>/. The file service at /api/files/<uuid> returns a presigned S3 URL to
anonymous users; the bucket itself is not public.

Each node is fetched with every scalar field the schema offers (found by introspection), plus
a link back to the case it belongs to, so records can be joined per dog. The data are public
and downloadable without login; see the data policy in AGENTS.md.

The data are messy in ways the analysis has to handle: dates come both as 2014-03-06 and as
11/21/2018, missing values are often empty strings, and some end dates use 3501-08-15 as a
"not recorded" sentinel.
"""

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://caninecommons.cancer.gov/v1/graphql/"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "data" / "icdc"
FILE_SERVICE = "https://caninecommons.cancer.gov/api/files/"
FILE_TYPES = ("Supplemental Data File", "Study Protocol")
PAGE_SIZE = 500

# Node type -> how each record links back to its case (and, for visits, its cycle). Scalar
# fields are added by introspection in scalar_fields().
LINKS = {
    "study": "",
    "case": "study { clinical_study_designation }",
    "demographic": "case { case_id }",
    "enrollment": "case { case_id }",
    "diagnosis": "case { case_id }",
    "prior_therapy": "enrollment { case { case_id } }",
    "cycle": "case { case_id }",
    "visit": "cycle { cycle_number } case { case_id }",
    "agent_administration": "visit { visit_id visit_date case { case_id } }",
    "adverse_event": "case { case_id }",
    "follow_up": "case { case_id }",
    "off_treatment": "case { case_id }",
}


def query(graphql: str) -> dict:
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"query": graphql}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        body = json.load(response)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def scalar_fields(node: str) -> list[str]:
    fields = query(f'{{ __type(name: "{node}") {{ fields {{ name type {{ kind ofType {{ kind }} }} }} }} }}')
    return [
        f["name"]
        for f in fields["__type"]["fields"]
        if f["type"]["kind"] in ("SCALAR", "ENUM")
        or (f["type"]["kind"] == "NON_NULL" and f["type"]["ofType"]["kind"] in ("SCALAR", "ENUM"))
    ]


def fetch_all(node: str, selection: str) -> list[dict]:
    records: list[dict] = []
    while True:
        page = query(f"{{ {node}(first: {PAGE_SIZE}, offset: {len(records)}) {{ {selection} }} }}")[node]
        records.extend(page)
        if len(page) < PAGE_SIZE:
            return records
        time.sleep(0.5)  # one request at a time, with a pause: this is a shared public service


def download_study_files(out: Path) -> list[dict]:
    files = fetch_all("file", "uuid file_name file_type file_size md5sum study { clinical_study_designation }")
    fetched = []
    for f in files:
        if f["file_type"] not in FILE_TYPES:
            continue
        study = (f.get("study") or {}).get("clinical_study_designation") or "unknown-study"
        target = out / "files" / study / f["file_name"]
        target.parent.mkdir(parents=True, exist_ok=True)
        # The API reports some MD5s in upper case, so compare case-insensitively.
        expected_md5 = f["md5sum"].lower()
        if not (target.exists() and hashlib.md5(target.read_bytes()).hexdigest() == expected_md5):
            with urllib.request.urlopen(FILE_SERVICE + f["uuid"], timeout=120) as response:
                signed_url = response.read().decode().strip()
            urllib.request.urlretrieve(signed_url, target)
            time.sleep(0.5)
            if hashlib.md5(target.read_bytes()).hexdigest() != expected_md5:
                raise RuntimeError(f"MD5 mismatch for {target}")
        print(f"file: {study}/{f['file_name']} ({target.stat().st_size} bytes, MD5 ok)")
        fetched.append({k: f[k] for k in ("uuid", "file_name", "file_type", "md5sum")} | {"study": study})
    return fetched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"output directory (default: {DEFAULT_OUT})")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    info = query("{ schemaVersion numberOfStudies numberOfCases }")
    counts = {}
    for node, links in LINKS.items():
        records = fetch_all(node, " ".join(scalar_fields(node)) + " " + links)
        distinct = len({json.dumps(r, sort_keys=True) for r in records})
        # Offset paging without an explicit order could repeat or skip records; flag it if so.
        note = "" if distinct == len(records) else f" ({len(records) - distinct} exact duplicates)"
        print(f"{node}: {len(records)} records{note}")
        (args.out / f"{node}.json").write_text(json.dumps(records, indent=1) + "\n")
        counts[node] = len(records)

    study_files = download_study_files(args.out)

    fetch_info = {
        "endpoint": ENDPOINT,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "schema_version": info["schemaVersion"],
        "number_of_studies": info["numberOfStudies"],
        "number_of_cases": info["numberOfCases"],
        "records": counts,
        "study_files": study_files,
    }
    (args.out / "fetch-info.json").write_text(json.dumps(fetch_info, indent=2) + "\n")
    if counts["case"] != info["numberOfCases"]:
        print(f"case count {counts['case']} differs from numberOfCases {info['numberOfCases']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
