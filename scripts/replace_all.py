import os
import re

def replace_brave_with_ibrowe_in_strings(content):
    # Only replace "Brave" with "iBrowe" inside string values
    return re.sub(
        r'"(.*?)" = "(.*?)";',
        lambda m: f'"{m.group(1)}" = "{m.group(2).replace("Brave", "iBrowe")}";',
        content
    )

def replace_brave_with_ibrowe_in_xml(content):
    # Temporarily extract <ph>...</ph> blocks
    ph_blocks = {}
    def extract_ph(match):
        key = f"__PH_BLOCK_{len(ph_blocks)}__"
        ph_blocks[key] = match.group(0)
        return key

    content = re.sub(r'<ph[^>]*>.*?</ph>', extract_ph, content, flags=re.DOTALL)

    # Replace Brave with iBrowe outside <ph> blocks
    content = re.sub(r'>([^<>]+)<', lambda m: f">{m.group(1).replace('Brave', 'iBrowe')}<", content)

    # Replace Brave in attributes (e.g., desc="")
    content = re.sub(
        r'(\b\w+=")([^"]*Brave[^"]*)(")',
        lambda m: m.group(1) + m.group(2).replace("Brave", "iBrowe") + m.group(3),
        content
    )

    # Restore original <ph> blocks
    for key, val in ph_blocks.items():
        content = content.replace(key, val.replace("Brave", "iBrowe"))  # Replace Brave inside <ph> if needed

    return content

def process_file(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        ext = os.path.splitext(input_file)[1].lower()

        if ext == ".strings":
            modified = replace_brave_with_ibrowe_in_strings(raw_content)
        elif ext in {".grd", ".grdp", ".xtb"}:
            modified = replace_brave_with_ibrowe_in_xml(raw_content)
        else:
            print(f"Skipped unsupported file: {input_file}")
            return False

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(modified)

        print(f"Processed: {input_file} → {output_file}")
        return True

    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return False

def replace_recursive_all(source_folder, dest_folder, skip_existing=True):
    processed = skipped = failed = 0
    extensions = {'.strings', '.grd', '.grdp', '.xtb'}

    for root, _, files in os.walk(source_folder):
        for file in files:
            if not any(file.lower().endswith(ext) for ext in extensions):
                continue

            rel_path = os.path.relpath(root, source_folder)
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_folder, rel_path, file)

            if skip_existing and os.path.exists(dst_file):
                print(f"Skipped: {dst_file}")
                skipped += 1
                continue

            if process_file(src_file, dst_file):
                processed += 1
            else:
                failed += 1

    print(f"\nSummary:\nProcessed: {processed}, Skipped: {skipped}, Failed: {failed}")

if __name__ == "__main__":
    source_folder = os.path.abspath("/Users/koeyl/Projects/ibrowe-core/src/translates")
    dest_folder = os.path.abspath("/Users/koeyl/Projects/ibrowe-core/src/translates")
    replace_recursive_all(source_folder, dest_folder, skip_existing=False)