import os
import re
import argparse

# 📁 โฟลเดอร์หลัก
root_dir = '../src'

SUPPORTED_EXTENSIONS = ['.grd', '.grdp', '.xtb']

parser = argparse.ArgumentParser()
parser.add_argument('--ext', type=str, choices=SUPPORTED_EXTENSIONS, required=True)
args = parser.parse_args()
file_extension = args.ext

# ✅ Pattern
message_pattern = re.compile(r'(<message\b[^>]*?>)(.*?)(</message>)', re.DOTALL)
translation_pattern = re.compile(r'(<translation\s+id="\d+">)(.*?)(</translation>)', re.DOTALL)
desc_pattern = re.compile(r'(desc\s*=\s*")(.*?)(")', re.DOTALL)
ph_with_ex_pattern = re.compile(r'(<ph\b[^>]*?>.*?</ph>)', re.DOTALL)
ex_pattern = re.compile(r'(<ex>)(.*?)(</ex>)', re.DOTALL)

# ✅ แทน Brave → iBrowe
def replace_brave(text):
    return (
        text.replace('Brave', 'iBrowe')
        .replace('brave', 'ibrowe')
        .replace('BRAVE', 'IBROWE')
    )

# 🔧 สำหรับ <ex> ใน <ph>
def replace_ex_in_ph(ph_block):
    return ex_pattern.sub(lambda m: f"{m.group(1)}{replace_brave(m.group(2))}{m.group(3)}", ph_block)

# ✅ สำหรับ .grd และ .grdp
def replace_grd_message(match):
    open_tag, body, close_tag = match.groups()

    if not any(word in body for word in ['Brave', 'brave', 'BRAVE']) and 'desc="' not in open_tag:
        return match.group(0)

    open_tag = desc_pattern.sub(lambda m: f'{m.group(1)}{replace_brave(m.group(2))}{m.group(3)}', open_tag)

    parts = re.split(ph_with_ex_pattern, body)
    new_parts = []
    for part in parts:
        if part.startswith('<ph'):
            new_parts.append(replace_ex_in_ph(part))
        else:
            new_parts.append(replace_brave(part))

    return f"{open_tag}{''.join(new_parts)}{close_tag}"

# ✅ สำหรับ .xtb
def replace_xtb_translation(match):
    open_tag, body, close_tag = match.groups()
    parts = re.split(r'(<ph\b[^>]*?/>)', body)
    new_parts = []
    for part in parts:
        if part.startswith('<ph'):
            new_parts.append(part)
        else:
            new_parts.append(replace_brave(part))
    return f"{open_tag}{''.join(new_parts)}{close_tag}"

# ✅ ทำงานกับแต่ละไฟล์
def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if file_extension in ['.grd', '.grdp']:
            new_content = message_pattern.sub(replace_grd_message, content)
        else:
            new_content = translation_pattern.sub(replace_xtb_translation, content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'✅ Updated: {file_path}')
        else:
            print(f'➖ No change: {file_path}')
    except Exception as e:
        print(f'❌ ERROR at {file_path}: {e}')

# 🔁 วนทุกไฟล์
for subdir, _, files in os.walk(root_dir):
    for file in files:
        if file.endswith(file_extension):
            process_file(os.path.join(subdir, file))

print(f"\n🎯 Done processing all '{file_extension}' files.")