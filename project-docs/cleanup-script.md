# Project Cleanup Script for TrueCred

This script will help you clean up unnecessary files and organize your project structure.

## Step 1: Backup Important Files

Before deleting anything, create a backup of potentially important files:

```powershell
# Create backup directory
mkdir -p "C:\Users\Shubham Gupta\GitHub\TrueCred\project-backup"

# Back up any important files from truecred-backend
Copy-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\truecred-backend\contracts\*.sol" -Destination "C:\Users\Shubham Gupta\GitHub\TrueCred\project-backup\contracts\" -Recurse -Force
```

## Step 2: Remove Redundant Backend Folder

After backing up any valuable files:

```powershell
# Remove the entire truecred-backend folder
Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\truecred-backend" -Recurse -Force
```

## Step 3: Clean Backend Folder

Remove unnecessary files from the backend folder:

```powershell
# Remove backup-existing folder
Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\backup-existing" -Recurse -Force

# Remove duplicate setup scripts (keep .py versions)
Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\setup_blockchain.bat" -Force
Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\setup_blockchain.sh" -Force
Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\setup_ipfs.bat" -Force
Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\setup_ipfs.sh" -Force

# Remove standalone test files (keep structured tests in tests/)
Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\test_*.py" -Force
```

## Step 4: Organize Backend Scripts

Move scripts to appropriate folders:

```powershell
# Create scripts folder if it doesn't exist
mkdir -p "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\scripts"

# Move setup scripts to scripts folder
Move-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\setup_*.py" -Destination "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\scripts\" -Force
```

## Step 5: Clean Frontend Folder

Remove unnecessary files from the frontend folder:

```powershell
# Remove unused component files (verify these are unused before removing)
# Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\frontend\src\components\unused\*" -Recurse -Force

# Remove draft or temporary files
Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\frontend\*.temp.*" -Force
Remove-Item -Path "C:\Users\Shubham Gupta\GitHub\TrueCred\frontend\*.draft.*" -Force
```

## Step 6: Organize Frontend Structure

```powershell
# Create organized folders if they don't exist
mkdir -p "C:\Users\Shubham Gupta\GitHub\TrueCred\frontend\src\features"
mkdir -p "C:\Users\Shubham Gupta\GitHub\TrueCred\frontend\src\layouts"
mkdir -p "C:\Users\Shubham Gupta\GitHub\TrueCred\frontend\src\hooks"
```

## Step 7: Commit Changes

After cleaning up, commit your changes:

```powershell
# Add all changes
git add .

# Commit with cleanup message
git commit -m "Project cleanup: remove redundant files and organize structure"

# Push to remote repository
git push
```

## Notes:

1. Always review files before deletion to ensure no important code is lost
2. If you're uncertain about a file, move it to the backup folder instead of deleting it
3. This script provides general guidance - adjust the paths and files based on your project's specific needs
4. Consider running parts of this script manually and reviewing the results before proceeding to the next step
