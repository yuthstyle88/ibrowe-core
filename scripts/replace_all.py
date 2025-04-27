import os
import xml.etree.ElementTree as ET

SEARCH_TEXT = "Brave"
REPLACE_TEXT = "iBrowe"

def process_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    changed = False

    for message in root.iter("message"):
        # 1. แก้ text ตรง <message> ถ้ามี
        if message.text and SEARCH_TEXT in message.text:
            message.text = message.text.replace(SEARCH_TEXT, REPLACE_TEXT)
            changed = True

        # 2. แก้ text ใน <ph> และ <ex> ที่อยู่ใต้ <message>
        for child in message:
            if child.tag in {"ph", "ex"} and child.text:
                if SEARCH_TEXT in child.text:
                    child.text = child.text.replace(SEARCH_TEXT, REPLACE_TEXT)
                    changed = True

        # 3. แก้ attribute desc ของ <message> ถ้ามี
        if "desc" in message.attrib and SEARCH_TEXT in message.attrib["desc"]:
            message.attrib["desc"] = message.attrib["desc"].replace(SEARCH_TEXT, REPLACE_TEXT)
            changed = True

    if changed:
        # Save ทับไฟล์เดิม
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        print(f"Modified and saved: {file_path}")

def scan_folder(folder):
    for root_dir, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".grdp") or file.endswith(".xtb") or file.endswith(".strings") or file.endswith(".grd") or file.endswith(".pak"):
                full_path = os.path.join(root_dir, file)
                process_file(full_path)

if __name__ == "__main__":
    translates_source_path = os.path.abspath("../src/translates")
    scan_folder(translates_source_path)
