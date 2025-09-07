#!/usr/bin/env bash
set -euo pipefail

### --- CONFIG ---
SRC_1024="${1:-$HOME/Desktop/AppIcon_1024.png}"  # พาธไฟล์ PNG 1024x1024
APP="/Applications/iBrowe.app"                   # พาธแอปรันจริง
ASSETS_ROOT="$HOME/Desktop/MyIcon.xcassets"
ICONSET="$ASSETS_ROOT/AppIcon.appiconset"
OUTDIR="/tmp/iBrowe_AppIconAssets"
MIN_OS="12.0"
CODESIGN_ID="Developer ID Application: 108 PLAZA COMPANY LIMITED (D8FP7GS222)"
### -------------

# ตรวจไฟล์ต้นฉบับ
if [[ ! -f "$SRC_1024" ]]; then
  # Try common fallbacks using the provided naming
  for cand in \
    ./ZZZZPackedAsset-1.0_Normal.png \
    ../ZZZZPackedAsset-1.0_Normal.png \
    "$HOME/Desktop/ZZZZPackedAsset-1.0_Normal.png" \
    "$HOME/Desktop/MyIcon.xcassets/AppIcon.appiconset/ZZZZPackedAsset-1.0_Normal.png"; do
      if [[ -f "$cand" ]]; then SRC_1024="$cand"; break; fi
  done
fi
if [[ ! -f "$SRC_1024" ]]; then
  echo "✗ ไม่พบไฟล์ 1024x1024: $SRC_1024"
  echo "วิธีใช้: ./make_ibrowe_assets.sh /path/to/AppIcon_1024.png (หรือวาง ZZZZPackedAsset-1.0_Normal.png ไว้ข้างสคริปต์)"
  exit 1
fi

# หาเครื่องมือ Xcode
ACTOOL="$(xcrun -f actool || true)"
if [[ -z "${ACTOOL}" ]]; then
  echo "✗ ไม่พบ xcode command line tools (actool). ติดตั้ง Xcode/CLT ก่อน"; exit 1
fi

echo "→ สร้าง/ใช้ .xcassets ที่มีอยู่ และแตกไซส์ถ้าจำเป็น..."
rm -rf "$OUTDIR"
mkdir -p "$ICONSET"

HAVE_SET=0
if [[ -f "$ICONSET/appicon_16_Normal.png" && -f "$ICONSET/appicon_32_Normal.png" && \
      -f "$ICONSET/appicon_32_Normal@2x.png" && -f "$ICONSET/appicon_128_Normal.png" && \
      -f "$ICONSET/appicon_256_Normal.png" && -f "$ICONSET/appicon_256_Normal@2x.png" && \
      -f "$ICONSET/appicon_512_Normal@2x.png" && -f "$ICONSET/ZZZZPackedAsset-1.0_Normal.png" ]]; then
  HAVE_SET=1
fi

if [[ "$HAVE_SET" -eq 0 ]]; then
  # สร้างขนาดมาตรฐาน macOS (ทั้ง 1x และ 2x)
  cp "$SRC_1024"               "$ICONSET/ZZZZPackedAsset-1.0_Normal.png"   # 1024 (512@2x)
  sips -Z 512  "$SRC_1024" --out "$ICONSET/appicon_512_Normal.png" >/dev/null
  sips -Z 256  "$SRC_1024" --out "$ICONSET/appicon_256_Normal.png" >/dev/null
  sips -Z 128  "$SRC_1024" --out "$ICONSET/appicon_128_Normal.png" >/dev/null
  sips -Z 64   "$SRC_1024" --out "$ICONSET/appicon_32_Normal@2x.png" >/dev/null
  sips -Z 32   "$SRC_1024" --out "$ICONSET/appicon_32_Normal.png" >/dev/null
  sips -Z 16   "$SRC_1024" --out "$ICONSET/appicon_16_Normal.png" >/dev/null

  # 2x ที่เหลือ
  cp "$ICONSET/ZZZZPackedAsset-1.0_Normal.png" "$ICONSET/appicon_512_Normal@2x.png"   # 512@2x = 1024
  cp "$ICONSET/appicon_512_Normal.png"          "$ICONSET/appicon_256_Normal@2x.png"   # 256@2x = 512
  # 128@2x จะอ้างถึง 256_Normal.png ผ่าน Contents.json (ไม่ต้องสร้างไฟล์ใหม่)
  # 16@2x จะอ้างถึง 32_Normal.png ผ่าน Contents.json (ไม่ต้องสร้างไฟล์ใหม่)
fi

if [[ ! -f "$ICONSET/appicon_512_Normal.png" ]]; then
  if [[ -f "$ICONSET/appicon_256_Normal@2x.png" ]]; then
    cp "$ICONSET/appicon_256_Normal@2x.png" "$ICONSET/appicon_512_Normal.png"
  elif [[ -f "$ICONSET/ZZZZPackedAsset-1.0_Normal.png" ]]; then
    sips -Z 512 "$ICONSET/ZZZZPackedAsset-1.0_Normal.png" --out "$ICONSET/appicon_512_Normal.png" >/dev/null
  else
    sips -Z 512 "$SRC_1024" --out "$ICONSET/appicon_512_Normal.png" >/dev/null
  fi
fi

# เขียน Contents.json (ครบ 1x/2x)
cat > "$ICONSET/Contents.json" <<'JSON'
{
  "images": [
    { "idiom": "mac", "size": "16x16",   "scale": "1x", "filename": "appicon_16_Normal.png" },
    { "idiom": "mac", "size": "16x16",   "scale": "2x", "filename": "appicon_32_Normal.png" },
    { "idiom": "mac", "size": "32x32",   "scale": "1x", "filename": "appicon_32_Normal.png" },
    { "idiom": "mac", "size": "32x32",   "scale": "2x", "filename": "appicon_32_Normal@2x.png" },
    { "idiom": "mac", "size": "128x128", "scale": "1x", "filename": "appicon_128_Normal.png" },
    { "idiom": "mac", "size": "128x128", "scale": "2x", "filename": "appicon_256_Normal.png" },
    { "idiom": "mac", "size": "256x256", "scale": "1x", "filename": "appicon_256_Normal.png" },
    { "idiom": "mac", "size": "256x256", "scale": "2x", "filename": "appicon_256_Normal@2x.png" },
    { "idiom": "mac", "size": "512x512", "scale": "1x", "filename": "appicon_512_Normal.png" },
    { "idiom": "mac", "size": "512x512", "scale": "2x", "filename": "appicon_512_Normal@2x.png" },
    { "idiom": "mac", "size": "1024x1024", "scale": "1x", "filename": "ZZZZPackedAsset-1.0_Normal.png" }
  ],
  "info": { "version": 1, "author": "xcode" }
}
JSON

mkdir -p "$OUTDIR"
echo "→ คอมไพล์ Assets.car..."
xcrun actool "$ASSETS_ROOT" \
  --compile "$OUTDIR" \
  --platform macosx \
  --minimum-deployment-target "$MIN_OS" \
  --app-icon AppIcon \
  --output-partial-info-plist "$OUTDIR/partial.plist"

# → บันทึกไฟล์ Assets.car ไว้ที่ Desktop (หรือกำหนด DEST เองได้ก่อนรัน)
DEST="${DEST:-$HOME/Desktop/Assets.car}"
cp "$OUTDIR/Assets.car" "$DEST"
echo "✅ สร้าง Assets.car เสร็จ: $DEST"
exit 0