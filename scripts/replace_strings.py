import os
import re

def replace_brave_with_ibrowe_in_strings(content):
    def replace_in_value(match):
        key = match.group(1)
        value = match.group(2).replace("Brave", "iBrowe")
        return f'"{key}" = "{value}";'

    return re.sub(r'"(.*?)" = "(.*?)";', replace_in_value, content, flags=re.DOTALL)

def process_strings_file(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        modified = replace_brave_with_ibrowe_in_strings(content)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(modified)

        print(f"Processed: {input_file} → {output_file}")
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return False

def process_all_strings(source_folder, dest_folder, skip_existing=True):
    processed = skipped = failed = 0

    for root, _, files in os.walk(source_folder):
        for file in files:
            if not file.lower().endswith('.strings'):
                continue

            rel_path = os.path.relpath(root, source_folder)
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_folder, rel_path, file)

            if skip_existing and os.path.exists(dst_file):
                print(f"Skipped: {dst_file}")
                skipped += 1
                continue

            if process_strings_file(src_file, dst_file):
                processed += 1
            else:
                failed += 1

    print(f"\nSummary:\nProcessed: {processed}, Skipped: {skipped}, Failed: {failed}")

if __name__ == "__main__":
    source_folder = "/Users/yongyutjantaboot/CLionProjects/brave-browser/src/ibrowe/src/translates"
    dest_folder = "/Users/yongyutjantaboot/CLionProjects/brave-browser/src/ibrowe/src/translates"
    process_all_strings(source_folder, dest_folder, skip_existing=False)