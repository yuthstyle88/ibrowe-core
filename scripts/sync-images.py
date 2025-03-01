import os
import shutil

def force_sync_folders(source_path, destination_path):
    # Check if both source and destination paths exist
    if not os.path.exists(source_path) or not os.path.exists(destination_path):
        print("One of the folders does not exist.")
        return

    for root, dirs, files in os.walk(source_path):
        relative_path = os.path.relpath(root, source_path)
        target_dir = os.path.join(destination_path, relative_path)

        # Create the target directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        for file_name in files:
            src_file = os.path.join(root, file_name)
            dest_file = os.path.join(target_dir, file_name)

            # Check if destination file exists and is the same size as source file
            if (os.path.exists(dest_file) and 
                os.path.getsize(src_file) == os.path.getsize(dest_file)):
                print(f"File '{dest_file}' already exists and is up-to-date.")
                continue

            shutil.copy2(src_file, dest_file)
    
    print("Force synchronization completed.")

if __name__ == "__main__":
    # Define source and destination folders
    source_folder = "../patches/images"
    destination_folder = "../../brave"

    force_sync_folders(source_folder, destination_folder)
