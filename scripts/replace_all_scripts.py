import os
import re

# กำหนด root directory ที่ต้องการประมวลผล
root_dir = '/Users/yongyutjantaboot/CLionProjects/ibrowe-browser/src/brave/ios/brave-ios/Sources'

# กำหนดนามสกุลไฟล์ที่ต้องการประมวลผล
file_extension = '.strings'

# กำหนด regex pattern
# for file_extension = '.swift'
# pattern = r'(value:\s*"[^"]*")|(comment:\s*"[^"]*")'
# for file_extension = '.strings'
pattern = r'=\s*"((?:[^"\\]|\\.)*)(")'

def replace_brave(match):
    value = match.group(1)

    updated_value = (
        value.replace('Brave', 'iBrowe')
        .replace('BRAVE', 'IBROWE')
        .replace('brave', 'ibrowe')
        .replace('"', r'\"')  # escape quote ภายใน
        .rstrip(r'\"')        # กัน quote ปิดเกิน (ถ้ามี)
    )

    # ✅ ถ้าไม่มีการเปลี่ยนแปลง → คืนค่าดั้งเดิม
    if value == updated_value:
        return match.group(0)

    return f'= "{updated_value}";'

# ฟังก์ชันสำหรับประมวลผลไฟล์
def process_file(file_path):
    try:
        # อ่านเนื้อหาไฟล์
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # แทนที่โดยใช้ regex และฟังก์ชัน callback
        new_content = re.sub(pattern, replace_brave, content)

        # บันทึกไฟล์ถ้ามีการเปลี่ยนแปลง
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f'ไฟล์ถูกอัปเดต: {file_path}')
        else:
            print(f'ไม่มีการเปลี่ยนแปลง: {file_path}')
    except Exception as e:
        print(f'เกิดข้อผิดพลาดที่ {file_path}: {e}')

# เดินทางผ่านโฟลเดอร์และโฟลเดอร์ย่อยทั้งหมด
for subdir, _, files in os.walk(root_dir):
    for file in files:
        if file.endswith(file_extension):
            file_path = os.path.join(subdir, file)
            process_file(file_path)

print('การประมวลผลเสร็จสิ้น!')
