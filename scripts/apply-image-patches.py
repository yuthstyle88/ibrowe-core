import os
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_destination_path():
    return os.path.abspath("../../brave")

def copy_back_files(source_folder, dest_folder):
    count = 0

    for root, dirs, files in os.walk(source_folder):
        # Exclude directories that start with '.' or contain "node_modules"
        dirs[:] = [d for d in dirs if not d.startswith(".") and "node_modules" not in d]

        if not files:
            continue  # Skip empty directories

        relative_path = os.path.relpath(root, source_folder)
        target_folder = os.path.join(dest_folder, relative_path)

        os.makedirs(target_folder, exist_ok=True)

        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(target_folder, file)

            try:
                shutil.copy2(source_file, dest_file)
                count += 1
                if count % 100 == 0:
                    logging.info(f"Copied back {count} files so far...")
            except Exception as e:
                logging.error(f"Error copying back {source_file} to {dest_file}: {e}")

    logging.info(f"Copied back {count} files successfully!")

if __name__ == "__main__":
    source_root = os.path.abspath("../patches/images/src/brave")
    brave_destination = get_destination_path()

    if os.path.exists(source_root):
        copy_back_files(source_root, brave_destination)
    else:
        logging.error("Source folder does not exist.")
