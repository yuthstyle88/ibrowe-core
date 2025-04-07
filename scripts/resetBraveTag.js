const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs-extra');

const resetBraveTag = () => {
  const braveDir = path.join(__dirname, '..', 'src', 'brave');
  const packageJsonPath = path.join(__dirname, '..', 'package.json');
  
  try {
    // Get the original tag from package.json
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const originalTag = packageJson.config.projects['brave-core'].tag;

    console.log(`Switching back to original tag: ${originalTag}`);

    // Switch back to the original tag
    execSync(`git checkout ${originalTag}`, { cwd: braveDir });

    console.log('Successfully switched back to original tag');
  } catch (error) {
    console.error('Error switching back to original tag:', error.message);
    process.exit(1);
  }
};

resetBraveTag(); 