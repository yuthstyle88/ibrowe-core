#!/usr/bin/env python3
"""
Automated script to update ibrowe-core from brave-core releases.

This script automates the workflow:
1. Download specified brave-core version from GitHub
2. Extract and compare files with ibrowe-core
3. Copy new/changed files (images and translations)
4. Update package.json with version info
5. Identify images that are logo/branding (for manual review)
6. Run replacement scripts

Usage:
    python scripts/update_from_brave.py --version v1.91.13
    python scripts/update_from_brave.py --version v1.91.13 --chrome-tag 146.0.7680.178
    python scripts/update_from_brave.py --version v1.91.13 --check-images-only

Requirements:
    - Python 3.x
    - requests library (`pip install requests`)

Author: Claude
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
IBROWE_ROOT = SCRIPT_DIR.parent
SRC_DIR = IBROWE_ROOT / "src"
IMAGES_DIR = SRC_DIR / "images"
TRANSLATES_DIR = SRC_DIR / "translates"
PACKAGE_JSON = IBROWE_ROOT / "package.json"

# Image extensions to process
IMAGE_EXTENSIONS = {".png", ".svg", ".ico", ".icns", ".icon", ".gif", ".jpg", ".jpeg", ".webp", ".xpm"}
TRANSLATE_EXTENSIONS = {".grd", ".grdp", ".xtb", ".pak", ".strings"}

# Patterns that indicate logo/branding images (should be kept/updated)
BRANDING_PATTERNS = [
    # Product logos
    r"product_logo",
    r"product_brand",
    r"branding",
    r"app_icon",
    # Installers
    r"installer_welcome",
    r"win/header",  # Windows installer header
    r"win/wizard",  # Windows installer wizard
    # Platform app icons
    r"mac/app_icon",
    r"ios/app_icon",
    r"android.*ic_launcher",
    r"chromium_logo",
    r"brave.*logo",
    r"about_credits",
    # Brave-specific branding graphics
    r"brave_web_discovery",
    r"brave_search_conversion",
    r"brave_speedreader_graphic",
    r"brave_ads.*graphic",
    r"brave_onboarding",
    r"brave_rewards.*graphic",
    r"brave.*banner",
    r"brave.*welcome",
    # Leo AI
    r"leo.*logo",
    r"product.*leo",
    # IPFS and other product logos
    r"ipfs_logo",
    r"wallet.*logo",
]

# Patterns that indicate generic UI icons (not branding, can be removed)
GENERIC_UI_PATTERNS = [
    r"btn_",
    r"button_",
    r"icon_arrow",
    r"icon_close",
    r"icon_menu",
    r"icon_check",
    r"icon_plus",
    r"icon_minus",
    r"icon_delete",
    r"icon_refresh",
    r"icon_settings",
    r"icon_search",
    r"icon_back",
    r"icon_forward",
    r"icon_home",
    r"icon_star",
    r"icon_bookmark",
    r"icon_download",
    r"icon_upload",
    r"icon_copy",
    r"icon_paste",
    r"icon_edit",
    r"icon_add",
    r"icon_remove",
    r"icon_expand",
    r"icon_collapse",
    r"chevron",
    r"dropdown",
    r"toolbar_",
    r"tab_",
    r"omnibox",
    r"location_bar",
]


def download_file(url: str, dest_path: Path, description: str = "file") -> bool:
    """Download a file from URL with progress indication."""
    print(f"Downloading {description}...")
    print(f"  URL: {url}")

    try:
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urlopen(request)

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 8192

        with open(dest_path, "wb") as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end="", flush=True)

        print(f"\n  Downloaded to: {dest_path}")
        return True

    except (URLError, HTTPError) as e:
        print(f"\n  Error downloading: {e}")
        return False


def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def extract_brave_core(zip_path: Path, extract_dir: Path) -> Path:
    """Extract brave-core zip and return the root directory."""
    print(f"Extracting {zip_path}...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # Find the extracted directory (usually brave-core-<version>)
    extracted_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
    if extracted_dirs:
        return extracted_dirs[0]
    return extract_dir


def compare_and_copy_files(source_dir: Path, dest_dir: Path, extensions: set, dry_run: bool = False) -> dict:
    """
    Compare files between source and destination, copy new/changed files.
    Returns dict with counts: {'new': int, 'changed': int, 'unchanged': int, 'copied': int}
    """
    stats = {"new": 0, "changed": 0, "unchanged": 0, "copied": 0}
    files_to_copy = []

    for root, _, files in os.walk(source_dir):
        # Skip hidden and node_modules directories
        if "/." in root or "\\." in root or "node_modules" in root:
            continue

        for file in files:
            if not any(file.lower().endswith(ext) for ext in extensions):
                continue

            source_file = Path(root) / file
            relative_path = source_file.relative_to(source_dir)
            dest_file = dest_dir / relative_path

            if not dest_file.exists():
                stats["new"] += 1
                files_to_copy.append((source_file, dest_file, "NEW"))
            else:
                source_hash = get_file_hash(source_file)
                dest_hash = get_file_hash(dest_file)

                if source_hash != dest_hash:
                    stats["changed"] += 1
                    files_to_copy.append((source_file, dest_file, "CHANGED"))
                else:
                    stats["unchanged"] += 1

    # Print summary first
    if files_to_copy:
        print(f"\n  Found {len(files_to_copy)} files to copy:")
        print(f"    - NEW: {stats['new']}")
        print(f"    - CHANGED: {stats['changed']}")
        print(f"    - UNCHANGED: {stats['unchanged']}")

        if not dry_run:
            print(f"\n  Copying files...")
            for source_file, dest_file, status in files_to_copy:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                print(f"    [{status}] {source_file.relative_to(source_dir)}")
                stats["copied"] += 1
    else:
        print(f"  No new or changed files found.")

    return stats


def is_branding_image(file_path: Path) -> bool:
    """Check if an image file is likely a logo/branding image."""
    path_str = str(file_path).lower().replace("\\", "/")

    # Check if it matches branding patterns
    for pattern in BRANDING_PATTERNS:
        if re.search(pattern, path_str, re.IGNORECASE):
            return True

    return False


def is_generic_ui_image(file_path: Path) -> bool:
    """Check if an image file is likely a generic UI icon."""
    path_str = str(file_path).lower().replace("\\", "/")
    filename = file_path.name.lower()

    # Check if it matches generic UI patterns
    for pattern in GENERIC_UI_PATTERNS:
        if re.search(pattern, path_str, re.IGNORECASE) or re.search(pattern, filename, re.IGNORECASE):
            return True

    return False


def analyze_images(images_dir: Path) -> dict:
    """
    Analyze images and categorize them as branding or generic UI.
    Returns dict with lists of files in each category.
    """
    categories = {
        "branding": [],      # Logo/branding images - should be kept/updated
        "generic_ui": [],    # Generic UI icons - can be removed
        "unknown": [],       # Unclear - needs manual review
    }

    for root, _, files in os.walk(images_dir):
        # Skip hidden and node_modules directories
        if "/." in root or "\\." in root or "node_modules" in root:
            continue

        for file in files:
            if not any(file.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                continue

            file_path = Path(root) / file

            if is_branding_image(file_path):
                categories["branding"].append(file_path)
            elif is_generic_ui_image(file_path):
                categories["generic_ui"].append(file_path)
            else:
                categories["unknown"].append(file_path)

    return categories


def remove_generic_ui_images(images_dir: Path, dry_run: bool = True) -> list:
    """
    Remove images that are identified as generic UI icons.
    Returns list of removed files.
    """
    removed = []

    for root, _, files in os.walk(images_dir):
        if "/." in root or "\\." in root or "node_modules" in root:
            continue

        for file in files:
            if not any(file.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                continue

            file_path = Path(root) / file

            if is_generic_ui_image(file_path) and not is_branding_image(file_path):
                if dry_run:
                    print(f"  [WOULD REMOVE] {file_path.relative_to(images_dir)}")
                else:
                    file_path.unlink()
                    print(f"  [REMOVED] {file_path.relative_to(images_dir)}")
                removed.append(file_path)

    return removed


def update_package_json(version: str, chrome_tag: str = None) -> bool:
    """Update package.json with new version and chrome tag."""
    try:
        with open(PACKAGE_JSON, "r") as f:
            package_data = json.load(f)

        # Update version (remove 'v' prefix if present)
        clean_version = version.lstrip("v")
        old_version = package_data.get("version", "")
        package_data["version"] = clean_version

        # Update chrome tag if provided
        if chrome_tag:
            if "config" not in package_data:
                package_data["config"] = {}
            if "projects" not in package_data["config"]:
                package_data["config"]["projects"] = {}
            if "chrome" not in package_data["config"]["projects"]:
                package_data["config"]["projects"]["chrome"] = {}
            if "tag" not in package_data["config"]["projects"]["chrome"]:
                package_data["config"]["projects"]["chrome"]["tag"] = {}

            old_tag = package_data["config"]["projects"]["chrome"].get("tag", "")
            package_data["config"]["projects"]["chrome"]["tag"] = chrome_tag

            print(f"  Version: {old_version} -> {clean_version}")
            print(f"  Chrome tag: {old_tag} -> {chrome_tag}")
        else:
            print(f"  Version: {old_version} -> {clean_version}")

        # Write back to file
        with open(PACKAGE_JSON, "w") as f:
            json.dump(package_data, f, indent=2)
            f.write("\n")  # Add trailing newline

        return True

    except Exception as e:
        print(f"  Error updating package.json: {e}")
        return False


def run_replacement_scripts():
    """Run the replacement scripts to update branding strings."""
    scripts = [
        ("replace_all_scripts.py", ["--ext", ".grd"]),
        ("replace_all_scripts.py", ["--ext", ".grdp"]),
        ("replace_all_scripts.py", ["--ext", ".xtb"]),
        ("replace_strings.py", []),
    ]

    for script_name, args in scripts:
        script_path = SCRIPT_DIR / script_name
        if script_path.exists():
            print(f"\n  Running {script_name}...")
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path)] + args,
                    cwd=SCRIPT_DIR,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"    Done")
                else:
                    print(f"    Error: {result.stderr}")
            except Exception as e:
                print(f"    Error running script: {e}")
        else:
            print(f"\n  Warning: {script_name} not found, skipping...")


def get_chrome_tag_from_brave_package(package_json_path: Path) -> str:
    """Extract chrome tag from brave-core's package.json."""
    try:
        with open(package_json_path, "r") as f:
            data = json.load(f)

        return data.get("config", {}).get("projects", {}).get("chrome", {}).get("tag", "")
    except Exception as e:
        print(f"  Warning: Could not read chrome tag from brave-core: {e}")
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="Update ibrowe-core from brave-core releases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download specific version and update everything
  python scripts/update_from_brave.py --version v1.91.13

  # Specify chrome tag manually
  python scripts/update_from_brave.py --version v1.91.13 --chrome-tag 146.0.7680.178

  # Only check and report on images
  python scripts/update_from_brave.py --check-images

  # Remove generic UI images (not branding)
  python scripts/update_from_brave.py --remove-generic-images
        """
    )

    parser.add_argument(
        "--version", "-v",
        help="Brave-core version to download (e.g., v1.91.13)"
    )
    parser.add_argument(
        "--chrome-tag", "-c",
        help="Chromium tag to use (auto-detected from brave-core if not specified)"
    )
    parser.add_argument(
        "--check-images",
        action="store_true",
        help="Only analyze and report on images (no download)"
    )
    parser.add_argument(
        "--remove-generic-images",
        action="store_true",
        help="Remove generic UI images (keeps only branding)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--skip-replacement",
        action="store_true",
        help="Skip running replacement scripts"
    )
    parser.add_argument(
        "--skip-package-update",
        action="store_true",
        help="Skip updating package.json"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("iBrowe Core Update Script")
    print("=" * 60)

    # Mode 1: Check images only
    if args.check_images:
        print("\n[1/1] Analyzing images...")
        print("-" * 40)

        categories = analyze_images(IMAGES_DIR)

        print(f"\n  BRANDING IMAGES ({len(categories['branding'])} files):")
        print("  These are logo/branding images that should be kept/updated:")
        for f in categories["branding"][:20]:  # Show first 20
            print(f"    - {f.relative_to(IMAGES_DIR)}")
        if len(categories["branding"]) > 20:
            print(f"    ... and {len(categories['branding']) - 20} more")

        print(f"\n  GENERIC UI IMAGES ({len(categories['generic_ui'])} files):")
        print("  These are generic UI icons that can be removed:")
        for f in categories["generic_ui"][:20]:
            print(f"    - {f.relative_to(IMAGES_DIR)}")
        if len(categories["generic_ui"]) > 20:
            print(f"    ... and {len(categories['generic_ui']) - 20} more")

        print(f"\n  UNKNOWN IMAGES ({len(categories['unknown'])} files):")
        print("  These need manual review:")
        for f in categories["unknown"][:20]:
            print(f"    - {f.relative_to(IMAGES_DIR)}")
        if len(categories["unknown"]) > 20:
            print(f"    ... and {len(categories['unknown']) - 20} more")

        print("\n" + "=" * 60)
        print("Summary:")
        print(f"  Branding: {len(categories['branding'])}")
        print(f"  Generic UI: {len(categories['generic_ui'])}")
        print(f"  Unknown: {len(categories['unknown'])}")
        print("=" * 60)
        return 0

    # Mode 2: Remove generic images
    if args.remove_generic_images:
        print("\n[1/1] Removing generic UI images...")
        print("-" * 40)

        if args.dry_run:
            print("  DRY RUN - no files will be removed\n")

        removed = remove_generic_ui_images(IMAGES_DIR, dry_run=args.dry_run)

        print(f"\n  {'Would remove' if args.dry_run else 'Removed'} {len(removed)} files")
        return 0

    # Mode 3: Full update from brave-core
    if not args.version:
        print("Error: --version is required for full update")
        parser.print_help()
        return 1

    version = args.version.lstrip("v")
    version_with_v = f"v{version}"

    # Step 1: Download brave-core
    print(f"\n[1/5] Downloading brave-core {version_with_v}...")
    print("-" * 40)

    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="brave-core-"))
    zip_path = temp_dir / f"brave-core-{version}.zip"

    # GitHub release URL
    download_url = f"https://github.com/brave/brave-core/archive/refs/tags/{version_with_v}.zip"

    if not download_file(download_url, zip_path, f"brave-core {version_with_v}"):
        print("Failed to download brave-core")
        shutil.rmtree(temp_dir)
        return 1

    # Step 2: Extract and analyze
    print(f"\n[2/5] Extracting and analyzing...")
    print("-" * 40)

    brave_core_dir = extract_brave_core(zip_path, temp_dir)
    print(f"  Extracted to: {brave_core_dir}")

    # Get chrome tag from brave-core package.json
    brave_package_json = brave_core_dir / "package.json"
    if brave_package_json.exists():
        detected_chrome_tag = get_chrome_tag_from_brave_package(brave_package_json)
        if detected_chrome_tag:
            print(f"  Detected Chrome tag: {detected_chrome_tag}")
            if not args.chrome_tag:
                args.chrome_tag = detected_chrome_tag

    # Step 3: Copy new/changed files
    print(f"\n[3/5] Copying files to ibrowe-core...")
    print("-" * 40)

    # Copy images
    print("\n  Processing images...")
    brave_images_dir = brave_core_dir
    image_stats = compare_and_copy_files(
        brave_images_dir, IMAGES_DIR, IMAGE_EXTENSIONS, dry_run=args.dry_run
    )

    # Copy translations
    print("\n  Processing translations...")
    if TRANSLATES_DIR.exists():
        translate_stats = compare_and_copy_files(
            brave_core_dir, TRANSLATES_DIR, TRANSLATE_EXTENSIONS, dry_run=args.dry_run
        )
    else:
        print(f"  Warning: {TRANSLATES_DIR} does not exist, skipping translations")

    # Step 4: Update package.json
    if not args.skip_package_update:
        print(f"\n[4/5] Updating package.json...")
        print("-" * 40)

        if args.dry_run:
            print(f"  DRY RUN - would update:")
            print(f"    version: {version}")
            if args.chrome_tag:
                print(f"    chrome.tag: {args.chrome_tag}")
        else:
            if not update_package_json(version, args.chrome_tag):
                print("  Failed to update package.json")
    else:
        print(f"\n[4/5] Skipping package.json update...")

    # Step 5: Run replacement scripts
    if not args.skip_replacement:
        print(f"\n[5/5] Running replacement scripts...")
        print("-" * 40)

        if args.dry_run:
            print("  DRY RUN - would run:")
            print("    - replace_all_scripts.py --ext .grd")
            print("    - replace_all_scripts.py --ext .grdp")
            print("    - replace_all_scripts.py --ext .xtb")
            print("    - replace_strings.py")
        else:
            run_replacement_scripts()
    else:
        print(f"\n[5/5] Skipping replacement scripts...")

    # Cleanup
    print(f"\nCleaning up temp files...")
    shutil.rmtree(temp_dir)

    # Summary
    print("\n" + "=" * 60)
    print("Update Complete!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  Version: {version}")
    if args.chrome_tag:
        print(f"  Chrome tag: {args.chrome_tag}")
    print(f"  Images - New: {image_stats['new']}, Changed: {image_stats['changed']}")
    print(f"\nNext steps:")
    print("  1. Review the changes")
    print("  2. Run: python scripts/update_from_brave.py --check-images")
    print("  3. Manually update logo/branding images if needed")
    print("  4. Run: python scripts/update_from_brave.py --remove-generic-images --dry-run")
    print("  5. If satisfied, run without --dry-run to actually remove")

    return 0


if __name__ == "__main__":
    sys.exit(main())