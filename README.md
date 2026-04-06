# iBrowe Core

This repository contains files originally from the Brave Browser project
(https://github.com/brave/brave-browser), licensed under the Mozilla Public License 2.0 (MPL-2.0).

The files included here have been copied and modified only for branding purposes
(e.g., renaming "Brave" to "iBrowe"). No functional changes or new features have been introduced.

This repository is not affiliated with or endorsed by Brave Software.

See the LICENSE file for more information.

## Scripts

### copyFileToBrave.js

Utility script for syncing files between iBrowe and Brave directories using checksum comparison.

**Prerequisites:**
- The `brave` repository must be located at `../../brave/` (sibling to this repo)
- Requires brave build utilities (`brave/build/commands/lib/util` and `config`)

**Functions:**

| Function | Description |
|----------|-------------|
| `copyFileToBrave()` | Copies images and translation files from iBrowe to Brave |
| `copyFileToiBrowe()` | Copies translation files (.strings, .grdp, .grd, .xtb) from Brave to iBrowe |

**Usage:**

```javascript
const { copyFileToBrave, copyFileToiBrowe } = require('./scripts/copyFileToBrave.js');

copyFileToBrave();   // iBrowe → Brave
copyFileToiBrowe();  // Brave → iBrowe (translations only)
```

**Features:**
- Checksum comparison to skip unchanged files
- Recursive directory copying
- File extension filtering

---

### apply-image-patches.py

Copies image and translation files from iBrowe to the Brave repository.

**Usage:**
```bash
python scripts/apply-image-patches.py
```

**What it copies:**

| Source | Destination | Extensions |
|--------|-------------|------------|
| `src/images/src/brave` | `../../brave` | .icns, .ico, .icon, .xpm, .png, .gif, .svg, .jpg, .jpeg, .webp |
| `src/translates` | `../../brave` | .grd, .grdp, .xtb, .pak, .strings |

---

### convert_icons.py

Converts Brave `.icon` files to PNG format using Cairo graphics library.

**Prerequisites:**
- Python with `cairo` package installed (`pip install pycairo`)

**Usage:**
```bash
python scripts/convert_icons.py <source_dir> <output_dir>
```

**Example:**
```bash
python scripts/convert_icons.py src/brave/icons output/png_icons
```

**Supported Commands:**
- `MOVE_TO`, `LINE_TO`, `CUBIC_TO`, `CLOSE`
- `R_LINE_TO`, `H_LINE_TO`, `V_LINE_TO`
- `PATH_COLOR_ARGB` for colors
- `CANVAS_DIMENSIONS` for sizing

---

### convert_to_png.sh

Shell script that converts `.icon` files to PNG via SVG intermediate format.

**Prerequisites:**
- ImageMagick (`magick` command)

**Usage:**
```bash
# First, copy icon files to output/icon_files
mkdir -p output/icon_files
find src -name "*.icon" -exec cp {} output/icon_files/ \;

# Then run the conversion
bash scripts/convert_to_png.sh
```

**Output:**
- `output/svg_files/` - Intermediate SVG files
- `output/png_icon_files/` - Final PNG files

---

### copy_files.sh

Simple script to collect all `.icon` files from `src` into a single folder.

**Usage:**
```bash
bash scripts/copy_files.sh
```

**Output:** `output/icon_files/`

---

### icon2svg.py

Converts Brave `.icon` format to SVG. Supports comprehensive path commands.

**Usage:**
```bash
python scripts/icon2svg.py input.icon output.svg
```

**Supported Commands:**
- Canvas: `CANVAS_DIMENSIONS`
- Paths: `NEW_PATH`, `CLOSE`
- Movement: `MOVE_TO`, `R_MOVE_TO`
- Lines: `LINE_TO`, `R_LINE_TO`, `HLINE_TO`, `VLINE_TO`, `R_H_LINE_TO`, `R_V_LINE_TO`
- Curves: `CUBIC_TO`, `CUBIC_TO_SHORTHAND`, `R_CUBIC_TO`, `R_QUADRATIC_TO`
- Arcs: `ARC_TO`, `R_ARC_TO`
- Shapes: `CIRCLE`
- Styling: `FILL`, `STROKE`, `STROKE_WIDTH`, `PATH_COLOR_ARGB`, `FILL_RULE_NONZERO`, `FILL_RULE_EVENODD`

---

### replace_all_scripts.py

Replaces "Brave" with "iBrowe" in translation files (.grd, .grdp, .xtb).

**Usage:**
```bash
python scripts/replace_all_scripts.py --ext <extension>
```

**Options:**
- `--ext .grd` - Process .grd files
- `--ext .grdp` - Process .grdp files
- `--ext .xtb` - Process .xtb files

**Example:**
```bash
python scripts/replace_all_scripts.py --ext .grd
python scripts/replace_all_scripts.py --ext .xtb
```

**What it replaces:**
- `Brave` → `iBrowe`
- `brave` → `ibrowe`
- `BRAVE` → `IBROWE`

**Directory:** Scans `../src` recursively

---

### replace_strings.py

Replaces "Brave" with "iBrowe" in macOS `.strings` files.

**Usage:**
Edit the source/destination paths in the script, then:
```bash
python scripts/replace_strings.py
```

**File Format:**
```
"key" = "Brave value";  →  "key" = "iBrowe value";
```

---

### svg2icon.py

Bidirectional converter between `.icon` and `.svg` formats.

**Usage:**
```bash
# Icon to SVG
python scripts/svg2icon.py input.icon output.svg

# SVG to Icon
python scripts/svg2icon.py input.svg output.icon
```

**Supported SVG Path Commands:**
- `M/m` - Move to
- `L/l` - Line to
- `H/h` - Horizontal line
- `V/v` - Vertical line
- `C/c` - Cubic Bezier
- `S/s` - Smooth cubic
- `A/a` - Arc
- `Z/z` - Close path

---

### sync-images.py

Copies translation files from Brave repository to iBrowe.

**Usage:**
```bash
python scripts/sync-images.py
```

**What it copies:**

| Source | Destination | Extensions |
|--------|-------------|------------|
| `../../brave` | `../src/translates` | .grd, .grdp, .xtb, .pak, .strings |

**Features:**
- Excludes `.git` directories and `node_modules`
- Preserves directory structure

---

### update_from_brave.py

**Main script for automating the update workflow from brave-core releases.**

**Usage:**
```bash
# Download specific version and update everything
python scripts/update_from_brave.py --version v1.91.13

# Specify chrome tag manually
python scripts/update_from_brave.py --version v1.91.13 --chrome-tag 146.0.7680.178

# Only check and report on images (no download)
python scripts/update_from_brave.py --check-images

# Preview what generic UI images would be removed
python scripts/update_from_brave.py --remove-generic-images --dry-run

# Actually remove generic UI images (keeps only branding)
python scripts/update_from_brave.py --remove-generic-images
```

**Options:**
| Option | Description |
|--------|-------------|
| `--version, -v` | Brave-core version to download (e.g., v1.91.13) |
| `--chrome-tag, -c` | Chromium tag to use (auto-detected if not specified) |
| `--check-images` | Analyze and report on images (no download) |
| `--remove-generic-images` | Remove generic UI images (keeps only branding) |
| `--dry-run` | Show what would be done without making changes |
| `--skip-replacement` | Skip running replacement scripts |
| `--skip-package-update` | Skip updating package.json |

**Workflow:**
1. Downloads brave-core source from GitHub releases
2. Extracts and compares files with ibrowe-core
3. Copies new/changed files (images and translations)
4. Updates package.json with version and chrome tag
5. Runs replacement scripts (replace_all_scripts.py, replace_strings.py)
6. Identifies and can remove non-branding images

**Image Categories:**
| Category | Description |
|----------|-------------|
| Branding | Logo/branding images that should be kept/updated |
| Generic UI | Generic UI icons (arrows, buttons, etc.) that can be removed |
| Unknown | Images that need manual review |

---

## Quick Reference

| Task | Command |
|------|---------|
| **Update from brave-core** | `python scripts/update_from_brave.py --version v1.91.13` |
| **Check images (branding vs generic)** | `python scripts/update_from_brave.py --check-images` |
| **Remove generic UI images** | `python scripts/update_from_brave.py --remove-generic-images` |
| Copy iBrowe → Brave (JS) | `node -e "require('./scripts/copyFileToBrave.js').copyFileToBrave()"` |
| Copy Brave → iBrowe (JS) | `node -e "require('./scripts/copyFileToBrave.js').copyFileToiBrowe()"` |
| Copy iBrowe → Brave (Python) | `python scripts/apply-image-patches.py` |
| Copy Brave → iBrowe translations | `python scripts/sync-images.py` |
| Replace branding in .grd files | `python scripts/replace_all_scripts.py --ext .grd` |
| Replace branding in .grdp files | `python scripts/replace_all_scripts.py --ext .grdp` |
| Replace branding in .xtb files | `python scripts/replace_all_scripts.py --ext .xtb` |
| Replace branding in .strings files | `python scripts/replace_strings.py` |
| Convert icon → SVG | `python scripts/icon2svg.py input.icon output.svg` |
| Convert SVG ↔ icon | `python scripts/svg2icon.py input output` |
| Convert icons → PNG | `python scripts/convert_icons.py src/ output/` |
