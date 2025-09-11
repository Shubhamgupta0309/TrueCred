# Backend Folder Consolidation Plan

## Current Situation

The project currently has two backend folders:

1. `backend/` - Active development folder with complete implementation
2. `truecred-backend/` - Appears to be mostly empty or unused

## Consolidation Steps

### 1. Backup (Before Making Changes)

```powershell
# Create a backup folder
mkdir -p "c:\Users\Shubham Gupta\GitHub\TrueCred\backup-truecred-backend"

# Copy all files from truecred-backend to the backup
Copy-Item -Path "c:\Users\Shubham Gupta\GitHub\TrueCred\truecred-backend\*" -Destination "c:\Users\Shubham Gupta\GitHub\TrueCred\backup-truecred-backend\" -Recurse
```

### 2. Extract Useful Files

The `truecred-backend/contracts` folder may contain valuable smart contract files.

```powershell
# Check if any files exist in the contracts folder
ls "c:\Users\Shubham Gupta\GitHub\TrueCred\truecred-backend\contracts"

# If there are valuable files, copy them to the main backend folder
Copy-Item -Path "c:\Users\Shubham Gupta\GitHub\TrueCred\truecred-backend\contracts\*" -Destination "c:\Users\Shubham Gupta\GitHub\TrueCred\backend\contracts\" -Recurse
```

### 3. Remove Redundant Folder

After confirming all valuable files are preserved:

```powershell
# Remove the truecred-backend folder
Remove-Item -Path "c:\Users\Shubham Gupta\GitHub\TrueCred\truecred-backend" -Recurse -Force
```

### 4. Update Documentation

- Update README.md to refer only to the `backend` folder
- Update any documentation or code references to use the correct path

### 5. Commit Changes

```powershell
git add .
git commit -m "Consolidate backend folders and remove redundant truecred-backend"
git push
```

## Note

If any unique code exists in `truecred-backend` that might be useful for future reference, consider preserving those specific files in a different location or in documentation before removing the folder.
