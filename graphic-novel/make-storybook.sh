#! /usr/bin/env bash
#
# This script is used to collect all "[a-z]*.md" docs from the `graphic-novel` directory.
# It writes an ordered concatenation of these files to `_storybook.md` in the `graphic-novel` directory.

# Exit on error or failed pipe
set -eo pipefail

# Define paths
GRAPHIC_NOVEL_DIR="graphic-novel"
OUTPUT_FILE="$GRAPHIC_NOVEL_DIR/_storybook.md"

# Create or clear the output file
cat "$GRAPHIC_NOVEL_DIR/_visual-style.md" >"$OUTPUT_FILE"

# Find all markdown files in the graphic-novel directory, excluding the 'book' subfolder,
# sort them, and concatenate their contents
find "$GRAPHIC_NOVEL_DIR" -type f -name "[a-z]*.md" \
        -not -path "$GRAPHIC_NOVEL_DIR/book/*" | sort | while read -r file; do
    echo "Processing $file..."
    cat "$file" >> "$OUTPUT_FILE"
    echo -e "\n\n" >> "$OUTPUT_FILE"  # Add two newlines between files
done

echo "All files have been concatenated into $OUTPUT_FILE"
ls -1lh "$OUTPUT_FILE"
