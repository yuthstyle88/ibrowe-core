const fs = require("fs");
const path = require("path");
const util = require('../../brave/build/commands/lib/util')
function copyRecursiveSync(src, dest) {
    if (!fs.existsSync(src)) {
        console.error(❌ Not found : '${src}');
        return;
    }

    const stats = fs.statSync(src);

    if (stats.isDirectory()) {

        // คัดลอกไฟล์และโฟลเดอร์ทั้งหมดใน src
        const files = fs.readdirSync(src);
        for (const file of files) {
            const srcPath = path.join(src, file);
            const destPath = path.join(dest, file);
            copyRecursiveSync(srcPath, destPath); // เรียกตัวเองซ้ำ
        }
    } else {
        if (!fs.existsSync(dest) ||
            util.calculateFileChecksum(src) != util.calculateFileChecksum(dest)) {
            fs.copySync(src, dest)
            console.log(✅ Copy : ${src} -> ${dest});
        }
    }
}
const ibroweImages = path.resolve(dirname, '..', 'src', 'ibrowe', 'src' , 'images')
const ibroweTranslates = path.resolve(dirname, '..', 'src', 'ibrowe', 'src' , 'translates')
const braveCoreDir = path.resolve(__dirname, '..', 'src', 'brave')
function copyFileToBrave() {
    copyRecursiveSync(ibroweImages, braveCoreDir);
    copyRecursiveSync(ibroweTranslates, braveCoreDir);
}
module.exports = { copyFileToBrave };