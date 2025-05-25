#! /usr/bin/env bash
set -e

git checkout HEAD docs/changed.md
echo >>docs/changed.md
git log --pretty=format: --name-only --since='2 months ago' recipes/ \
 | egrep '/.+/' | cut -f2 -d/ | sort -u \
 | sed -r -e 's#^(.)(.+)$# * [\1\2](../\1/\1\2)#' >>docs/changed.md
echo -e "\n[last updated $(date --iso)]" >>docs/changed.md

cat docs/changed.md
