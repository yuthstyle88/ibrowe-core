import os
import shutil

def copy_brave_files(source_folder, destfolder, files_extensions, is_exist=False):
    """
    Copies files with specified extensions from source_folder to destfolder.

    - Does not create empty directories.
    """
    count = 0

    for root, _, files in os.walk(source_folder):
        # Filter files based on extensions
        files_to_copy = [file for file in files if any(file.lower().endswith(ext) for ext in files_extensions)]

        # **Skip this folder if it contains no matching files**
        if not files_to_copy:
            continue

        # Determine relative path and target folder
        relative_path = os.path.relpath(root, source_folder)
        target_folder = os.path.join(destfolder, relative_path)

        # **Create the folder only if it contains files to copy**
        os.makedirs(target_folder, exist_ok=True)

        # Copy files
        for file in files_to_copy:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(target_folder, file)

            try:
                if is_exist:
                    if not os.path.exists(dest_file):
                        shutil.copy2(source_file, dest_file)
                        count += 1
                else:
                    shutil.copy2(source_file, dest_file)
                    count += 1
            except Exception as e:
                print(f"Error copying file {source_file} to {dest_file}: {e}")

    print(f"Copied {count} files successfully from {source_folder} to {destfolder}!")

if __name__ == "__main__":
    # Source folders
    brave_source_root = os.path.abspath("/Users/koeyl/Projects/brave-core-1.77.101")

    destination_img_root = os.path.abspath("../src/images")
    destination_translates_source_root = os.path.abspath("../src/translates")

    if os.path.exists(brave_source_root):
        copy_brave_files(brave_source_root, destination_img_root, {".icns", ".ico", ".icon", ".xpm", ".png", ".gif", ".svg", ".jpg", ".jpeg", ".webp"}, True)
    else:
        print(f"Source folder does not exist: {brave_source_root}")

    if os.path.exists(brave_source_root):
        copy_brave_files(brave_source_root, destination_translates_source_root, {".grd", ".grdp", ".xtb", ".pak", ".strings"})
    else:
        print(f"Source folder does not exist: {brave_source_root}")
