# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Download openFDA Animal & Veterinary adverse-event reports for the given years.

Usage:
    uv run ideas/veterinary-adverse-events/download_openfda_animal.py --years 2025 2026

openFDA publishes one zipped JSON file per quarter, listed in the download manifest at
https://api.fda.gov/download.json. Files go to
data/openfda/animalandveterinary/event/<YYYYqN>/ (gitignored), and are unzipped beside the zip.
A quarter whose unzipped JSON already holds the record count the manifest lists is skipped.

openFDA data is a snapshot of FDA's current view, not a history: a report that received
follow-up information after it was first filed appears only in its latest form. The manifest's
export date is written to manifest-snapshot.json so analyses can say which snapshot they used.
"""

import argparse
import json
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MANIFEST_URL = "https://api.fda.gov/download.json"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "data" / "openfda" / "animalandveterinary" / "event"


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=120) as response:
        return json.load(response)


def count_records(json_path: Path) -> int:
    with json_path.open() as f:
        return len(json.load(f)["results"])


def quarter_key(partition: dict) -> str:
    # The file URL carries the quarter, e.g. .../animalandveterinary/event/2025q1/...
    return partition["file"].rstrip("/").split("/")[-2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--years", nargs="+", required=True, help="years to download, e.g. 2025 2026")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"output directory (default: {DEFAULT_OUT})")
    args = parser.parse_args()

    manifest = fetch_json(MANIFEST_URL)
    dataset = manifest["results"]["animalandveterinary"]["event"]
    partitions = sorted(
        (p for p in dataset["partitions"] if p["display_name"][:4] in args.years),
        key=quarter_key,
    )
    if not partitions:
        print(f"No partitions for years {args.years} in the manifest.", file=sys.stderr)
        return 1

    fetched = []
    failed = False
    for partition in partitions:
        quarter = quarter_key(partition)
        expected = int(partition["records"])
        directory = args.out / quarter
        directory.mkdir(parents=True, exist_ok=True)
        zip_path = directory / partition["file"].split("/")[-1]
        json_path = zip_path.with_suffix("")  # strips .zip, leaving .json

        if json_path.exists() and count_records(json_path) == expected:
            print(f"{quarter}: already present, {expected} records")
        else:
            print(f"{quarter}: downloading {partition['size_mb']} MB")
            urllib.request.urlretrieve(partition["file"], zip_path)
            with zipfile.ZipFile(zip_path) as archive:
                archive.extractall(directory)
            actual = count_records(json_path)
            status = "ok" if actual == expected else f"MISMATCH, manifest says {expected}"
            print(f"{quarter}: {actual} records ({status})")
            failed |= actual != expected
        fetched.append({"quarter": quarter, "records": expected, "file": partition["file"]})

    snapshot = {
        "manifest_url": MANIFEST_URL,
        "export_date": dataset["export_date"],
        "manifest_last_updated": manifest["meta"]["last_updated"],
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "license": manifest["meta"]["license"],
        "partitions": fetched,
    }
    (args.out / "manifest-snapshot.json").write_text(json.dumps(snapshot, indent=2) + "\n")
    print(f"Export date {dataset['export_date']}; wrote {args.out / 'manifest-snapshot.json'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
