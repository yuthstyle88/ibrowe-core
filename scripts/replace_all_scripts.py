import os
import re
import argparse

# 📁 ตำแหน่งโฟลเดอร์ที่จะประมวลผล
root_dir = '/home/yuth/temp/brave'

# ✅ รองรับไฟล์ .grd, .grdp, .xtb เท่านั้น
SUPPORTED_EXTENSIONS = ['.grd', '.grdp', '.xtb']

# 🎯 รับพารามิเตอร์ extension จาก command line
parser = argparse.ArgumentParser()
parser.add_argument('--ext', type=str, choices=SUPPORTED_EXTENSIONS, required=True,
                    help='File extension to process: .grd, .grdp, or .xtb')
args = parser.parse_args()
file_extension = args.ext

# ✅ Regex patterns
message_pattern = re.compile(r'(<message\b[^>]*?>)(.*?)(</message>)', re.DOTALL)
translation_pattern = re.compile(r'(<translation\s+id="\d+">)(.*?)(</translation>)', re.DOTALL)
desc_pattern = re.compile(r'(desc\s*=\s*")(.*?)(")', re.DOTALL)
ph_pattern = re.compile(r'(<ph\b[^>]*?>.*?</ph>)', re.DOTALL)
ex_pattern = re.compile(r'(<ex>)(.*?)(</ex>)', re.DOTALL)

# เลือก pattern ตาม extension
pattern = message_pattern if file_extension in ['.grd', '.grdp'] else translation_pattern

# 🔁 ฟังก์ชันแทนที่คำว่า Brave → iBrowe
def replace_brave(text):
    return (
        text.replace('Brave', 'iBrowe')
        .replace('brave', 'ibrowe')
        .replace('BRAVE', 'IBROWE')
    )

def replace_ex_content(ph_block):
    return ex_pattern.sub(lambda m: f"{m.group(1)}{replace_brave(m.group(2))}{m.group(3)}", ph_block)

# 🔧 สำหรับ .grd และ .grdp
def replace_grd_message(match):
    open_tag = match.group(1)
    body = match.group(2)
    close_tag = match.group(3)

    # ✅ ถ้าไม่เจอ Brave และไม่มี desc="..." → ข้าม
    if not any(x in body for x in ['Brave', 'brave', 'BRAVE']) and 'desc="' not in open_tag:
        return match.group(0)

    # ✅ แทนที่ใน desc
    open_tag = desc_pattern.sub(lambda m: f'{m.group(1)}{replace_brave(m.group(2))}{m.group(3)}', open_tag)

    # ✅ แยก <ph> ออกมาเพื่อแทน <ex> ภายใน
    parts = re.split(ph_pattern, body)
    new_parts = []
    for part in parts:
        if part.startswith('<ph'):
            new_parts.append(replace_ex_content(part))
        else:
            new_parts.append(replace_brave(part))

    return f"{open_tag}{''.join(new_parts)}{close_tag}"

# 🔧 สำหรับ .xtb
def replace_xtb_translation(match):
    open_tag = match.group(1)
    body = match.group(2)
    close_tag = match.group(3)

    if 'Brave' in body or 'brave' in body or 'BRAVE' in body:
        return f"{open_tag}{replace_brave(body)}{close_tag}"
    else:
        return match.group(0)

# 🔧 ประมวลผลไฟล์
def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if file_extension in ['.grd', '.grdp']:
            new_content = pattern.sub(replace_grd_message, content)
        else:
            new_content = pattern.sub(replace_xtb_translation, content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'✅ Updated: {file_path}')
        else:
            print(f'➖ No change: {file_path}')
    except Exception as e:
        print(f'❌ ERROR at {file_path}: {e}')

# 🔁 วนลูปประมวลผลทุกไฟล์
for subdir, _, files in os.walk(root_dir):
    for file in files:
        if file.endswith(file_extension):
            process_file(os.path.join(subdir, file))

print(f"\n🎯 Done processing all '{file_extension}' files.")