const fs = require("fs");
const path = require("path");
const util = require('../../brave/build/commands/lib/util')
const config = require('../../brave/build/commands/lib/config')
function copyRecursiveSync(src, dest) {
    if (!fs.existsSync(src)) {
        console.error(`❌ Not found : '${src}'`);
        return;
    }

    const stats = fs.statSync(src);

    if (stats.isDirectory()) {

        // คัดลอกไฟล์และโฟลเดอร์ทั้งหมดใน src
        const files = fs.readdirSync(src);
        for (const file of files) {
            const srcPath = path.join(src, file);
            const destPath = path.join(dest, file);
            copyRecursiveSync(srcPath, destPath);
        }
    } else {
        if (!fs.existsSync(dest)) {
            console.error(`❌ Not found : '${dest}' `);
            return;
        }
        if (util.calculateFileChecksum(src) != util.calculateFileChecksum(dest)) {
            fs.copyFileSync(src, dest)
            console.log(`✅ Copy : ${src} -> ${dest}`);
        }
    }
}
const ibroweImages = path.resolve(config.srcDir, 'ibrowe', 'src' , 'images')
const ibroweTranslates = path.resolve(config.srcDir, 'ibrowe', 'src' , 'translates')
const braveCoreDir = path.resolve(config.srcDir, 'brave')
function copyFileToBrave() {
    copyRecursiveSync(ibroweImages, braveCoreDir);
    copyRecursiveSync(ibroweTranslates, braveCoreDir);
}
module.exports = { copyFileToBrave };
