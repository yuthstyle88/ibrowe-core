import xml.etree.ElementTree as ET
import os

def replace_brave_with_ibrowe(xml_content):
    try:
        # Parse the XML content
        tree = ET.ElementTree(ET.fromstring(xml_content))
        root = tree.getroot()

        # Iterate through all <message> elements
        for message in root.findall(".//message"):
            # Replace 'Brave' with 'iBrowe' in the 'desc' attribute
            if message.get("desc"):
                message.set("desc", message.get("desc").replace("Brave", "iBrowe"))

            # Replace 'Brave' with 'iBrowe' in the inner text content
            if message.text:
                message.text = message.text.replace("Brave", "iBrowe")

            # Handle nested elements (e.g., <ph>) and their tails
            for child in message:
                if child.text:
                    child.text = child.text.replace("Brave", "iBrowe")
                if child.tail:
                    child.tail = child.tail.replace("Brave", "iBrowe")

        # Convert the modified tree back to a string, preserving comments
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str += '<!-- Modified by script: Replaced Brave with iBrowe -->\n'
        xml_str += ET.tostring(root, encoding='unicode').replace('ns0:', '').replace(':ns0', '')
        return xml_str
    except ET.ParseError:
        raise ValueError("Invalid XML format in the input content.")

def read_from_xml_file(input_file, output_file):
    try:
        # Read the XML content from the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
            xml_str = replace_brave_with_ibrowe(xml_content)
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml_str)
            print(f"Successfully processed: '{input_file}' -> '{output_file}'")
            return True
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return False
    except ValueError as e:
        print(f"Error processing '{input_file}': {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error processing '{input_file}': {str(e)}")
        return False

def replace_recursive_files(source_folder, dest_folder, skip_existing=True):
    """
    Recursively process .grdp and .grd files in source_folder and its subfolders,
    replace 'Brave' with 'iBrowe', and save modified files to dest_folder.

    Args:
        source_folder (str): Path to the source folder (e.g., '../src/translates').
        dest_folder (str): Path to the destination folder (e.g., '../src/translates_modified').
        skip_existing (bool): If True, skip files that already exist in the destination.

    Returns:
        tuple: (processed_count, skipped_count, failed_count)
    """
    processed_count = 0
    skipped_count = 0
    failed_count = 0
    files_extensions = ('.grdp', '.grd')

    try:
        # Validate source folder
        if not os.path.exists(source_folder):
            print(f"Error: Source folder '{source_folder}' does not exist.")
            return processed_count, skipped_count, failed_count

        # Check if any .grdp or .grd files exist
        has_files = False
        for root, _, files in os.walk(source_folder):
            if any(file.lower().endswith(ext) for file in files for ext in files_extensions):
                has_files = True
                break
        if not has_files:
            print(f"Warning: No .grdp or .grd files found in '{source_folder}' or its subfolders.")
            return processed_count, skipped_count, failed_count

        for root, _, files in os.walk(source_folder):
            # Filter files based on extensions
            files_to_process = [file for file in files if any(file.lower().endswith(ext) for ext in files_extensions)]

            # Skip this folder if it contains no matching files
            if not files_to_process:
                continue

            # Determine relative path and target folder
            relative_path = os.path.relpath(root, source_folder)
            target_folder = os.path.join(dest_folder, relative_path)

            # Process each matching file
            for file in files_to_process:
                source_file = os.path.join(root, file)
                dest_file = os.path.join(target_folder, file)

                try:
                    # Skip if destination file exists and skip_existing is True
                    if skip_existing and os.path.exists(dest_file):
                        print(f"Skipped: '{dest_file}' (already exists).")
                        skipped_count += 1
                        continue

                    # Process the file
                    if read_from_xml_file(source_file, dest_file):
                        processed_count += 1
                    else:
                        failed_count += 1

                except Exception as e:
                    print(f"Error processing '{source_file}' to '{dest_file}': {str(e)}")
                    failed_count += 1

        # Summary
        print(f"\nSummary:")
        print(f"Processed: {processed_count} files")
        print(f"Skipped: {skipped_count} files (already exist)")
        print(f"Failed: {failed_count} files")
        print(f"From '{source_folder}' to '{dest_folder}'.")
        return processed_count, skipped_count, failed_count

    except Exception as e:
        print(f"Error in replace_recursive_files: {str(e)}")
        return processed_count, skipped_count, failed_count

if __name__ == "__main__":
    # Define source and destination folders
    source_folder = os.path.abspath("/Users/koeyl/Projects/ibrowe-core/src/translates/app")
    dest_folder = os.path.abspath("/Users/koeyl/Projects/ibrowe-core/src/translates_modified")

    # Process all .grdp and .grd files recursively
    replace_recursive_files(source_folder, dest_folder, skip_existing=True)