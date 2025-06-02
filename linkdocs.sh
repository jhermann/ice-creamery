#! /usr/bin/env bash
set -e

find recipes -mindepth 1 -type d | \
while read dir; do
    name=$(basename "$dir")
    letter=$(tr a-z A-Z <<<"${name:0:1}")
    mkdir -p "docs/$letter"
    ln -nfs "../../$dir/README.md" "docs/$letter/$name.md"

    ( ls -1 "$dir"/*.{png,jpg} 2>/dev/null || : ) | \
    while read img; do
        mkdir -p "docs/$letter/$(basename "$dir")"
        ln -nfs "../../../$img" "docs/$letter/$(basename "$dir")/$(basename "$img")"
    done
done
