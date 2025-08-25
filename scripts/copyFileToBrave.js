const fs = require("fs");
const path = require("path");
const util = require('../../brave/build/commands/lib/util')
const config = require('../../brave/build/commands/lib/config')
function copyRecursiveSync(src, dest, extensions = []) {
    if (!fs.existsSync(src)) {
        console.error(`❌ Not found : '${src}'`);
        return;
    }

    const allowAll = !Array.isArray(extensions) || extensions.length === 0;
    const extSet = allowAll ? null : new Set(extensions.map(normalizeExt));

    const stats = fs.statSync(src);

    if (stats.isDirectory()) {
        // สร้างโฟลเดอร์ปลายทางถ้ายังไม่มี
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }

        // คัดลอกไฟล์และโฟลเดอร์ทั้งหมดใน src
        const files = fs.readdirSync(src);
        for (const file of files) {
            const srcPath = path.join(src, file);
            const destPath = path.join(dest, file);
            copyRecursiveSync(srcPath, destPath, extensions);
        }
    } else {
        // กรองตามนามสกุลไฟล์
        if (!allowAll) {
            const ext = path.extname(src).toLowerCase();
            if (!extSet.has(ext)) return;
        }

        // ให้แน่ใจว่าโฟลเดอร์ปลายทางมีอยู่
        const destDir = path.dirname(dest);
        if (!fs.existsSync(destDir)) {
            fs.mkdirSync(destDir, { recursive: true });
        }

        // ถ้าไฟล์ปลายทางยังไม่มี ให้ก๊อปเลย
        if (!fs.existsSync(dest)) {
            fs.copyFileSync(src, dest);
            console.log(`✅ Copy : ${src} -> ${dest}`);
            return;
        }

        // เทียบ checksum ก่อนคัดลอกทับ
        if (util.calculateFileChecksum(src) !== util.calculateFileChecksum(dest)) {
            fs.copyFileSync(src, dest);
            console.log(`✅ Copy : ${src} -> ${dest}`);
        }
    }

    function normalizeExt(ext) {
        if (!ext) return '';
        return ext.startsWith('.') ? ext.toLowerCase() : `.${ext.toLowerCase()}`;
    }
}

const ibroweImages = path.resolve(config.srcDir, 'ibrowe', 'src' , 'images')
const ibroweTranslates = path.resolve(config.srcDir, 'ibrowe', 'src' , 'translates')
const braveCoreDir = path.resolve(config.srcDir, 'brave')
function copyFileToBrave() {
    copyRecursiveSync(ibroweImages, braveCoreDir);
    copyRecursiveSync(ibroweTranslates, braveCoreDir);
}
function copyFileToiBrowe() {
    extension = ['.icon', '.png', '.jpg', '.svg', '.webp', '.json','.ico','.gif']
    copyRecursiveSync(braveCoreDir, ibroweImages, extension);
    extension = ['.strings', '.grdp', '.grd', '.xtb']
    copyRecursiveSync(braveCoreDir, ibroweTranslates, extension);
}
module.exports = { copyFileToBrave ,copyFileToiBrowe};
