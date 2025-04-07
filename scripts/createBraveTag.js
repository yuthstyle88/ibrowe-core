const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Get the current version from package.json
const packagePath = path.join(__dirname, '../package.json');
const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

// Get ibrowe-core tag directly (including the 'v' prefix)
const ibroweTag = packageJson.config.projects['ibrowe-core'].tag;

// Configuration
const config = {
  braveDir: path.join(__dirname, '../src/brave'),
  ibroweDir: path.join(__dirname, '../src/ibrowe'),
  tagName: ibroweTag, // Use the exact same tag as ibrowe-core
  branchName: `ibrowe/${ibroweTag}`,
  commitMessage: `Update to match iBrowe Core ${ibroweTag}`
};

console.log(`Creating tag ${config.tagName} in Brave source code...`);

function createBranchAndTag() {
  try {
    // Change to the Brave directory
    process.chdir(config.braveDir);
    
    // Create and checkout new branch if it doesn't exist
    try {
      execSync(`git checkout -b ${config.branchName}`, { stdio: 'inherit' });
      console.log(`Created and checked out new branch ${config.branchName}`);
    } catch (error) {
      // Branch might already exist
      try {
        execSync(`git checkout ${config.branchName}`, { stdio: 'inherit' });
        console.log(`Checked out existing branch ${config.branchName}`);
      } catch (checkoutError) {
        console.error('Error checking out branch:', checkoutError.message);
        process.exit(1);
      }
    }
    
    // Check if the tag already exists
    try {
      execSync(`git rev-parse --verify --quiet refs/tags/${config.tagName}`, { stdio: 'ignore' });
      console.log(`Tag ${config.tagName} already exists. Skipping tag creation.`);
    } catch (error) {
      // Tag doesn't exist, continue with creation
      
      // Check if there are any changes to commit
      let hasChanges = false;
      try {
        const status = execSync('git status --porcelain', { encoding: 'utf8' });
        hasChanges = status.trim().length > 0;
      } catch (error) {
        console.error('Error checking git status:', error.message);
      }
      
      if (hasChanges) {
        // Create a new commit with the current state
        execSync('git add .', { stdio: 'inherit' });
        execSync(`git commit -m "${config.commitMessage}"`, { stdio: 'inherit' });
      } else {
        // No changes, create an empty commit
        execSync(`git commit --allow-empty -m "${config.commitMessage}"`, { stdio: 'inherit' });
      }
      
      // Create the tag
      execSync(`git tag -a ${config.tagName} -m "Matching iBrowe Core ${ibroweTag}"`, { stdio: 'inherit' });
      console.log(`Successfully created tag ${config.tagName}`);
    }
    
    // Update package.json in brave directory to reflect new version
    const bravePackagePath = path.join(config.braveDir, 'package.json');
    if (fs.existsSync(bravePackagePath)) {
      const bravePackage = JSON.parse(fs.readFileSync(bravePackagePath, 'utf8'));
      const currentVersion = bravePackage.version;
      const newVersion = ibroweTag.replace('v', ''); // Remove 'v' prefix for package.json version
      
      // Only update if version is different
      if (currentVersion !== newVersion) {
        bravePackage.version = newVersion;
        fs.writeFileSync(bravePackagePath, JSON.stringify(bravePackage, null, 2));
        console.log(`Updated version in ${bravePackagePath} to ${bravePackage.version}`);
        
        // Check if there are changes to commit
        try {
          const status = execSync('git status --porcelain', { encoding: 'utf8' });
          if (status.trim().length > 0) {
            // Commit the package.json change
            execSync('git add package.json', { stdio: 'inherit' });
            execSync(`git commit -m "Update package.json version to ${bravePackage.version}"`, { stdio: 'inherit' });
          } else {
            console.log('No changes to package.json to commit');
          }
        } catch (error) {
          console.error('Error checking git status:', error.message);
        }
      } else {
        console.log(`Version in ${bravePackagePath} is already ${newVersion}`);
      }
    }
    
  } catch (error) {
    console.error('Error in branch/tag creation:', error.message);
    process.exit(1);
  } finally {
    // Change back to the original directory
    process.chdir(path.join(__dirname, '..'));
  }
}

// Run the script
createBranchAndTag(); 