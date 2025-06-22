import os
import shutil
import argparse

def copy_brave_files(source_folder, destfolder, files_extensions, check_existence=False):
    """
    Copies files with specified extensions from source_folder to destfolder.
    Skips files if they already exist in destination with the same name (if check_existence is True).
    """
    count = 0
    skipped = 0

    for root, _, files in os.walk(source_folder):
        files_to_copy = [file for file in files if any(file.lower().endswith(ext) for ext in files_extensions)]

        if not files_to_copy:
            continue

        relative_path = os.path.relpath(root, source_folder)
        target_folder = os.path.join(destfolder, relative_path)

        os.makedirs(target_folder, exist_ok=True)

        for file in files_to_copy:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(target_folder, file)
            
            if check_existence and os.path.exists(dest_file):
                skipped += 1
                continue

            try:
                shutil.copy2(source_file, dest_file)
                count += 1
            except Exception as e:
                print(f"Error copying {source_file} → {dest_file}: {e}")

    print(f"Copied {count} new files.")
    print(f"Skipped {skipped} existing files.")
    print(f"From: {source_folder} → To: {destfolder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Check for existing files before copying')
    args = parser.parse_args()

    brave_source_path = os.path.abspath("/Users/yongyutjantaboot/CLionProjects/translater/brave-core")
    translates_source_path = os.path.abspath("/Users/yongyutjantaboot/CLionProjects/translater/ibrowe-core")

    destination_root = os.path.abspath("../src/images")
    destination_language_root = os.path.abspath("../src/translates")

    if os.path.exists(brave_source_path):
        copy_brave_files(brave_source_path, destination_root, {
            ".icns", ".ico", ".icon", ".xpm", ".png", ".gif", ".svg", ".jpg", ".jpeg", ".webp"
        }, check_existence=True)
    else:
        print(f"Source folder not found: {brave_source_path}")

    if os.path.exists(brave_source_path):
        copy_brave_files(brave_source_path, destination_language_root, {
            ".grd", ".grdp", ".xtb", ".pak", ".strings"
        })
    else:
        print(f"Source folder not found: {brave_source_path}")
