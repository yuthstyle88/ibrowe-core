import os
import shutil

def get_brave_source_path():
    return "../brave"

def copy_brave_files(source_folder, destfolder, files_extensions):
    count = 0
    
    for root, dirs, files in os.walk(source_folder):
        # Exclude directories that start with '.' and node_modules
        dirs[:] = [d for d in dirs if not d.startswith(".") and "node_modules" not in d]

        # Check if any file in the current directory matches the desired extensions
        files_to_copy = [file for file in files if any(file.lower().endswith(ext) for ext in files_extensions)]

        # If no matching files, skip the folder
        if not files_to_copy:
            continue

        relative_path = os.path.relpath(root, source_folder)
        target_folder = os.path.join(destfolder, relative_path)

        os.makedirs(target_folder, exist_ok=True)

        # Copy specific file types
        for file in files_to_copy:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(target_folder, file)

            try:
                shutil.copy2(source_file, dest_file)
                count += 1
            except Exception as e:
                print(f"Error copying file {source_file} to {dest_file}: {e}")

    print(f"Copied {count} files successfully!")

if __name__ == "__main__":
    brave_source_path = get_brave_source_path()
    destination_root = os.path.join("..", "patches/images/src/brave")
    
    language_extensions = {".grd", ".grdp", ".xtb", ".pak", ".strings"}
    icon_image_extensions = {".icns", ".ico", ".icon", ".xpm", ".png", ".gif", ".svg", ".jpg", ".jpeg", ".webp"}

    if os.path.exists(brave_source_path):
        copy_brave_files(brave_source_path, destination_root, icon_image_extensions)
        copy_brave_files(brave_source_path, destination_language_root, language_extensions)
    else:
        print("Source folder does not exist.")
