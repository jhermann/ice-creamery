##! /usr/bin/env bash
W=640
H=900
GAP=0

rm -f ~/tmp/recipe*png
egrep -v img.+src README.md \
    | pandoc --to html5 | sed '/DIRECTIONS/,$d' >~/tmp/recipe.html \
    && chromium 2>~/tmp/recipe.log --headless --window-size=$(($W - $GAP)),$H --screenshot=$HOME/tmp/recipe-0.png ~/tmp/recipe.html
egrep -v img.+src README.md \
    | pandoc --to html5 | sed '/DIRECTIONS/,$!d' >~/tmp/recipe.html \
    && chromium 2>~/tmp/recipe.log --headless --window-size=$(($W - $GAP)),$H --screenshot=$HOME/tmp/recipe-1.png ~/tmp/recipe.html

#( cd ~/tmp && convert -crop 100%x50% recipe.png recipe.png )
identify ~/tmp/recipe*png
montage -geometry ${W}x${H}+0+0 ~/tmp/recipe-?.png "recipe.png"
identify "recipe.png"
wslview "recipe.png"
