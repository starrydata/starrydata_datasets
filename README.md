[IMPORTANT]

**Duplicated `sample_id` in datasets published between 2026-04-01 and 2026-09-04**

In these datasets the same `sample_id` can refer to samples belonging to **different papers**. Joining tables on `sample_id` alone will mix data from unrelated papers.

**Workaround:**

join on the pair `(SID, sample_id)`, which is unique.

**Corrected dataset:**

every `sample_id`, `figure_id` and `SID` is unique in [`starrydata_dataset_renumbered.zip`](https://drive.google.com/drive/folders/1OVMP7j61CJFwLtJ-qZFef9ko40Othayh) on Google Drive.

Identifiers that originated in the public Starrydata database were **not changed**, so existing analyses using those values remain valid. The fix will be applied to the live database in the week beginning 2026-09-07; datasets published after that date already include it.


# starrydata_datasets

Daily per-project splits of the [Starrydata2](https://starrydata.nims.go.jp/) dataset, with a browsable download page at **https://starrydata.github.io/starrydata_datasets/**.

Historically this repository also hosted the raw CSVs (from 2019/7/11 until 2022/12/22); those older archives are still available via git tags.

## Dataset repositories

| Repository | Description | Update schedule | Period |
|------------|-------------|-----------------|--------|
| [Google Drive](https://drive.google.com/drive/folders/1OVMP7j61CJFwLtJ-qZFef9ko40Othayh) | Latest full dataset (single ZIP) | Twice daily at 00:00 and 12:00 JST | from 2024/06/13 |
| [GitHub Releases (this repo)](https://github.com/starrydata/starrydata_datasets/releases) | Per-project splits + full dataset, as `.csv.gz` | Daily around 03:00 JST | from 2026/06/25 |
| [Figshare](https://figshare.com/projects/Starrydata_datasets/155129) | Archival snapshots | Daily until 2024/06/06, then monthly | from 2022/12/22 |
| [GitHub tags (this repo)](https://github.com/starrydata/starrydata_datasets/tags) | Legacy snapshots | As needed | 2019/7/11 – 2022/12/22 |

## What this repository does

Every day the `Daily split & release` workflow:

1. Downloads the latest full ZIP from Google Drive (`starrydata_dataset.zip`).
2. Runs `scripts/split.py`, which produces per-project files by looking at each row of `starrydata_curves.csv` and reading its `project_names` JSON array.
3. Publishes two GitHub Releases:
   - `data-YYYYMMDD` — the dated snapshot.
   - `latest` — recreated to always mirror the newest snapshot.
4. Commits `docs/manifest.json` to `master`, which triggers a GitHub Pages redeploy.

### Membership rules (per project)

Membership is defined **from curves outward**, so the counts match [starrydata.github.io/links/](https://starrydata.github.io/links/):

- **curves**: rows whose `project_names` array contains the project.
- **papers**: rows in `starrydata_papers.csv` whose `SID` appears in the project's curves.
- **samples**: rows in `starrydata_samples.csv` whose composite key `(SID, sample_id)` appears in the project's curves (`sample_id` alone is paper-local, not globally unique).
- **figures**: number of distinct non-empty `figure_id` values in the project's curves.

## Downloading

Every file lives under a **stable** URL that always points at the newest snapshot:

```
https://github.com/starrydata/starrydata_datasets/releases/latest/download/<FILENAME>
```

### Full dataset

| File | Contents |
|------|----------|
| `all_papers.csv.gz` | Every paper |
| `all_samples.csv.gz` | Every sample |
| `all_curves.csv.gz` | Every curve |

### Per-project

For each project (e.g. `ThermoelectricMaterials`, `BatteryMaterials`, `MagneticMaterials`, `OrganicThermoelectricMaterials`, …), three files:

- `<Project>_papers.csv.gz`
- `<Project>_samples.csv.gz`
- `<Project>_curves.csv.gz`

The canonical list of available projects and files is `manifest.json` (see below).

### Loading in Python

```python
import pandas as pd

BASE = "https://github.com/starrydata/starrydata_datasets/releases/latest/download"
curves = pd.read_csv(f"{BASE}/ThermoelectricMaterials_curves.csv.gz", compression="gzip")
```

### Opening in Excel

`.csv.gz` is gzipped — decompress first (`gunzip <file>` on macOS/Linux, or 7-Zip on Windows) and open the resulting `.csv`.

## manifest.json

`docs/manifest.json` is regenerated on every run and mirrored to https://starrydata.github.io/starrydata_datasets/manifest.json. Its schema:

```jsonc
{
  "generated_at": "2026-07-17T08:47:07+00:00",         // when this manifest was built (UTC ISO)
  "db_snapshot":  "2026-07-17 16:58:34 UTC+0900 (JST)", // upstream Starrydata DB snapshot time
  "source_zip":   "starrydata_dataset.zip",
  "totals": {                     // Whole-DB counts (match links page definitions)
    "papers":  17381,             //   unique non-empty SID in curves ("papers with data")
    "figures": 60228,             //   unique non-empty figure_id in curves
    "samples": 105260,            //   total rows in starrydata_samples.csv
    "curves":  234029             //   total rows in starrydata_curves.csv
  },
  "all_data": {
    "papers":  { "filename": "all_papers.csv.gz",  "rows": 56473,  "bytes": 9460869,  "sha256": "..." },
    "samples": { "filename": "all_samples.csv.gz", "rows": 105260, "bytes": 4675538,  "sha256": "..." },
    "curves":  { "filename": "all_curves.csv.gz",  "rows": 234029, "bytes": 43423914, "sha256": "..." }
  },
  "projects": {
    "ThermoelectricMaterials": {
      "papers":  { "filename": "...", "rows": ..., "bytes": ..., "sha256": "..." },
      "samples": { "filename": "...", "rows": ..., "bytes": ..., "sha256": "..." },
      "curves":  { "filename": "...", "rows": ..., "bytes": ..., "sha256": "..." },
      "counts":  { "papers": ..., "figures": ..., "samples": ..., "curves": ... }
    }
  }
}
```

The project list is **dynamic** — every project name that appears in any curve's `project_names` array shows up here. No hardcoded allowlist.

Other pages on starrydata.github.io consume this same manifest.

## Manual re-run

Web UI: [Run workflow](https://github.com/starrydata/starrydata_datasets/actions/workflows/daily-split.yml).

CLI:

```sh
gh workflow run "Daily split & release" -R starrydata/starrydata_datasets
```

The workflow has `concurrency: daily-split` so a manual run and the scheduled run will serialize, not collide.

## When the pipeline fails

The workflow opens an issue titled `Daily split pipeline failed` on the first failure, comments on it if it fails again, and auto-closes it on the next success. While an incident is open, the always-fresh full ZIP is still available directly from [Google Drive](https://drive.google.com/drive/folders/1OVMP7j61CJFwLtJ-qZFef9ko40Othayh).

## Layout

```
.github/workflows/daily-split.yml   # daily schedule + workflow_dispatch
scripts/
  split.py                          # ZIP → per-project CSV.gz + manifest.json
  requirements.txt
docs/
  index.html                        # Pages UI, renders from manifest.json alone
  manifest.json                     # latest snapshot metadata (auto-committed)
```

## Changelog

### 2026/07/17
- Rebuilt the Pages listing and Starrydata `links` page to read directly from this repo's daily `manifest.json`. New projects (e.g. `OrganicThermoelectricMaterials`) now appear the day they're added to the DB, instead of waiting for the monthly Figshare mirror. Added `totals` and per-project `counts` (including `figures`) to `manifest.json`.

### 2026/06/26
- Added per-project dataset downloads at https://starrydata.github.io/starrydata_datasets/. Each project can now be downloaded separately as `papers` / `samples` / `curves` files, alongside the full unsplit dataset.
- Compressed all downloads as gzipped CSV (`.csv.gz`) to reduce file size. Load directly with `pandas.read_csv(url, compression="gzip")` or decompress before opening in Excel.

### 2025/08/22
- Add `figure_name` field to curve dataset.

### 2024/07/04
- Excluded datasets with the data type "calculation" in the descriptor from the sample dataset and curve dataset. As of 2024/07/01 12:00:01 UTC+0900 (JST), there were [346 samples](https://github.com/starrydata/notebook/blob/0ab26b17a8046fe480b3649d9faad325688b61e2/check_sample_datatype/check_sample_datatype.ipynb).

### 2024/06/26
- Changed dataset file name prefix from `all` to `starrydata`. For example, `all_curves.csv` is now `starrydata_curves.csv`.
- Changed the file extension of the paper dataset from JSON to CSV for availability.
- Reduced the columns in the paper dataset to only those necessary for citation, reducing the file size from 400 MB to about 50 MB.
- Added `project_names` and `created_at` to the paper dataset.

### 2024/06/13
- The latest datasets are now uploaded to Google Drive.

### 2024/06/06
- Fixed the character corruption issue when users open `all_samples.csv` in certain applications, such as Excel, by adding a BOM.
- The upload schedule to Figshare has been changed from daily to monthly.

### 2024/05/22
- Fixed the incorrect timestamp format in the dataset. For example, corrected `"2024-05-17 00:00:01 JST+0900"` to `"2024-05-17 00:00:01 GMT+0900 (JST)"`.

### 2024/05/21
- The values in the XY value list were originally strings enclosed in double quotations. These double quotations were removed for easier analysis.
- e.g. `["299.8597", "324.8683"]` → `[299.8597, 324.8683]`

### 2024/05/16
- Added `updated_at`, `created_at`, and `composition_details` to `all_samples.csv`.

### 2022/12/22
- The dataset location was changed from this GitHub repository to [Figshare](https://figshare.com/projects/Starrydata_datasets/155129).
