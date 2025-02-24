#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📌 Script is running from: $SCRIPT_DIR"

# Define the patch directory (relative to the script)
PATCH_DIR="$SCRIPT_DIR/../patches"
echo "📂 Looking for patches in: $PATCH_DIR"

# Define the target repository where patches should be applied (relative to script)
TARGET_REPO="$SCRIPT_DIR/../../brave"
echo "📂 Target repository (where patches will be applied): $TARGET_REPO"

# Ensure the patch directory exists
if [ ! -d "$PATCH_DIR" ]; then
    echo "❌ ERROR: Patch directory '$PATCH_DIR' not found!"
    exit 1
fi

# Ensure the target repository exists
if [ ! -d "$TARGET_REPO" ]; then
    echo "❌ ERROR: Target repository '$TARGET_REPO' not found!"
    exit 1
fi

# Change to the target repository directory
cd "$TARGET_REPO" || { echo "❌ ERROR: Failed to switch to target directory: $TARGET_REPO"; exit 1; }

echo "✅ Successfully changed directory to: $(pwd)"
echo "🔄 Checking if the repository is a valid Git repository..."

# Ensure we're in a Git repository
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    echo "❌ ERROR: The target directory is not a valid Git repository!"
    exit 1
fi

echo "✅ Confirmed: This is a valid Git repository."

# Apply each patch file
PATCH_COUNT=0
APPLIED_COUNT=0
FAILED_COUNT=0

echo "🔍 Scanning for patch files in $PATCH_DIR..."
for patch in "$PATCH_DIR"/*.patch; do
    if [ -f "$patch" ]; then
        PATCH_COUNT=$((PATCH_COUNT + 1))
        PATCH_NAME=$(basename "$patch")

        echo "----------------------------------------------"
        echo "🔄 Applying patch: $PATCH_NAME"
        echo "📄 Patch location: $patch"

        # Check if the patch can be applied cleanly
        if git apply --check "$patch"; then
            echo "✅ Patch check successful. Applying the patch..."
            if git apply "$patch"; then
                echo "✅ SUCCESS: Patch applied successfully: $PATCH_NAME"
                APPLIED_COUNT=$((APPLIED_COUNT + 1))
            else
                echo "❌ ERROR: Failed to apply patch: $PATCH_NAME"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
        else
            echo "⚠️ WARNING: Patch $PATCH_NAME cannot be applied cleanly."
            echo "❌ ERROR: Skipping patch: $PATCH_NAME"
            FAILED_COUNT=$((FAILED_COUNT + 1))
        fi
    fi
done

# Summary of patch application
echo "----------------------------------------------"
echo "📊 Patch Application Summary"
echo "🔢 Total patches found: $PATCH_COUNT"
echo "✅ Successfully applied: $APPLIED_COUNT"
echo "❌ Failed to apply: $FAILED_COUNT"

# Final message
if [ "$FAILED_COUNT" -eq 0 ]; then
    echo "🎉 All patches applied successfully!"
else
    echo "⚠️ Some patches failed to apply. Please check the error messages above."
fi

echo "🔚 Patch application process completed."
