#! /usr/bin/env bash
#
# Purpose: Aggregate Markdown content from various project directories into summary files.
#
# - Collects all docs/info/*.md files into all-info.txt
# - Collects all recipes/*/README.md files into all-recipes.txt
# - Collects all wiki/*.md files into all-wiki.txt
#
# Usage: Run this script from the project root directory to update the summary files.

set -euo pipefail

head -9999 docs/info/*.md >all-info.txt
head -9999 recipes/*/README.md >all-recipes.txt
head -9999 wiki/*.md >all-wiki.txt

ls -lh all-*.txt
