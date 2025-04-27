import os
import re

SEARCH_TEXT = "Brave"
REPLACE_TEXT = "iBrowe"

def replace_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace แบบ text ธรรมดา (ไม่ parse XML เลย)
    if SEARCH_TEXT in content:
        content = content.replace(SEARCH_TEXT, REPLACE_TEXT)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Modified and saved: {file_path}")
    else:
        print(f"No Brave found in: {file_path}")

def scan_folder(folder):
    for root_dir, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".grdp") or file.endswith(".xml"):
                full_path = os.path.join(root_dir, file)
                replace_in_file(full_path)

if __name__ == "__main__":
    translates_source_path = os.path.abspath("../src/translates")
    scan_folder(translates_source_path)
