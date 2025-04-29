import os
import re

def replace_brave_with_ibrowe_in_strings(xml_str):
    """
    Replace 'Brave' with 'iBrowe' in .strings format content, ensuring placeholders like %@ are unaffected.
    """
    def replace_brave_in_string_content(content):
        """
        Helper function to replace 'Brave' with 'iBrowe' in the content of the string,
        excluding any placeholder markers like %@.
        """
        # Match the text between placeholders and replace 'Brave' with 'iBrowe' in that part
        return re.sub(r'([^%]*)Brave([^%]*)', r'\1iBrowe\2', content)

    # Regular expression to match lines in the .strings format
    # It assumes that the .strings file uses the format:
    # "key" = "value";
    xml_str = re.sub(r'"(.*?)" = "(.*?)";', lambda match: f'"{match.group(1)}" = "{replace_brave_in_string_content(match.group(2))}";', xml_str)

    return xml_str

def process_file_raw(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_str = f.read()

        replaced = replace_brave_with_ibrowe_in_strings(raw_str)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(replaced)

        print(f"Processed: {input_file} → {output_file}")
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return False

def replace_recursive_raw(source_folder, dest_folder, skip_existing=True):
    processed = skipped = failed = 0
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith('.strings'):  # Only process .strings files
                rel_path = os.path.relpath(root, source_folder)
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_folder, rel_path, file)

                if skip_existing and os.path.exists(dst_file):
                    print(f"Skipped: {dst_file}")
                    skipped += 1
                    continue

                if process_file_raw(src_file, dst_file):
                    processed += 1
                else:
                    failed += 1

    print(f"\nSummary:")
    print(f"Processed: {processed}, Skipped: {skipped}, Failed: {failed}")

if __name__ == "__main__":
    source_folder = os.path.abspath("/Users/koeyl/Projects/ibrowe-browser-1.77.101/src/ibrowe/src/translates")
    dest_folder = os.path.abspath("/Users/koeyl/Projects/ibrowe-browser-1.77.101/src/ibrowe/src/translates")

    replace_recursive_raw(source_folder, dest_folder, skip_existing=False)
