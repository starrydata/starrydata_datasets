#!/usr/bin/env python3
"""Split Starrydata all-data CSVs into per-project CSV.gz files.

Per-project membership is defined by the curves table:
  - curves: rows whose `project_names` JSON array contains the project name
  - papers: rows whose `SID` appears in the project's curves
  - samples: rows whose composite (SID, sample_id) appears in the project's curves
    (sample_id is paper-local, NOT globally unique, so SID is required)

Matches the counts shown on https://starrydata.github.io/links/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PAPER_CSV = "starrydata_papers.csv"
SAMPLE_CSV = "starrydata_samples.csv"
CURVE_CSV = "starrydata_curves.csv"
SNAPSHOT_TXT = "db_snapshot.txt"


def extract_zip(zip_path: Path, extract_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)


def project_names_of(value: object) -> list[str]:
    if not isinstance(value, str) or not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [x for x in dict.fromkeys(parsed) if isinstance(x, str)]


def gzip_write(df: pd.DataFrame, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False, compression="gzip")
    return dest.stat().st_size


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def split(zip_path: Path, out_dir: Path) -> dict:
    work = out_dir / "_extracted"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    extract_zip(zip_path, work)

    snapshot = (work / SNAPSHOT_TXT).read_text().strip() if (work / SNAPSHOT_TXT).exists() else ""

    print(f"[load] {PAPER_CSV}", file=sys.stderr)
    papers = pd.read_csv(work / PAPER_CSV, dtype=str, keep_default_na=False)
    print(f"[load] {SAMPLE_CSV}", file=sys.stderr)
    samples = pd.read_csv(work / SAMPLE_CSV, dtype=str, keep_default_na=False)
    print(f"[load] {CURVE_CSV}", file=sys.stderr)
    curves = pd.read_csv(work / CURVE_CSV, dtype=str, keep_default_na=False)

    curve_projects = curves["project_names"].map(project_names_of)
    all_projects: set[str] = set()
    for projs in curve_projects:
        all_projects.update(projs)
    projects_sorted = sorted(all_projects)
    print(f"[info] {len(projects_sorted)} projects detected from curves", file=sys.stderr)

    out_data = out_dir / "data"
    if out_data.exists():
        shutil.rmtree(out_data)
    out_data.mkdir(parents=True)

    sample_key = samples["SID"] + "\x00" + samples["sample_id"]

    all_data: dict[str, dict] = {}
    for kind, df in (("papers", papers), ("samples", samples), ("curves", curves)):
        fname = f"all_{kind}.csv.gz"
        fpath = out_data / fname
        size = gzip_write(df, fpath)
        all_data[kind] = {
            "filename": fname,
            "rows": int(len(df)),
            "bytes": size,
            "sha256": sha256(fpath),
        }
    print(
        f"[done] {'all (whole dataset)':40} papers={len(papers):6} samples={len(samples):6} curves={len(curves):7}",
        file=sys.stderr,
    )

    manifest: dict[str, dict] = {}
    for project in projects_sorted:
        mask = curve_projects.map(lambda ps, p=project: p in ps)
        c_sub = curves[mask]
        sid_set = set(c_sub["SID"].unique())
        curve_sample_keys = set((c_sub["SID"] + "\x00" + c_sub["sample_id"]).unique())
        p_sub = papers[papers["SID"].isin(sid_set)]
        s_sub = samples[sample_key.isin(curve_sample_keys)]

        files: dict[str, dict] = {}
        for kind, df in (("papers", p_sub), ("samples", s_sub), ("curves", c_sub)):
            fname = f"{project}_{kind}.csv.gz"
            fpath = out_data / fname
            size = gzip_write(df, fpath)
            files[kind] = {
                "filename": fname,
                "rows": int(len(df)),
                "bytes": size,
                "sha256": sha256(fpath),
            }
        print(
            f"[done] {project:40} papers={len(p_sub):6} samples={len(s_sub):6} curves={len(c_sub):7}",
            file=sys.stderr,
        )
        manifest[project] = files

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "db_snapshot": snapshot,
        "source_zip": zip_path.name,
        "all_data": all_data,
        "projects": manifest,
    }
    (out_dir / "manifest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"[write] {out_dir / 'manifest.json'}", file=sys.stderr)

    shutil.rmtree(work)
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    split(args.zip, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
