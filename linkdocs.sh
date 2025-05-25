#! /usr/bin/env bash
set -e

find recipes -mindepth 1 -type d | \
while read dir; do
    name=$(basename "$dir")
    letter=$(tr a-z A-Z <<<"${name:0:1}")
    mkdir -p "docs/$letter"
    ln -nfs "../../$dir/README.md" "docs/$letter/$name.md"
done
