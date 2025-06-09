#! /usr/bin/env bash
set -e

# Clean up broken symlinks
find docs/ -xtype l | xargs -I+ rm "+"

find recipes -mindepth 1 -type d | \
while read dir; do
    name=$(basename "$dir")
    letter=$(tr a-z A-Z <<<"${name:0:1}")
    mkdir -p "docs/$letter"

    if [ "$name" = "Toppings" ]; then
        cp "$dir/README.md" "docs/$letter/$name.md"

        ( ls -1 "$dir"/recipe-*.md 2>/dev/null || : ) | sort | \
        while read include; do
            cat "$include" >>"docs/$letter/$name.md"
        done
    else
        ln -nfs "../../$dir/README.md" "docs/$letter/$name.md"
    fi

    ( ls -1 "$dir"/*.{png,jpg,jpeg} 2>/dev/null || : ) | \
    while read img; do
        mkdir -p "docs/$letter/$(basename "$dir")"
        ln -nfs "../../../$img" "docs/$letter/$(basename "$dir")/$(basename "$img")"
    done
done
