#!/bin/sh
FILES=$1/*
for f in $FILES
do
    filename=$(basename "$f")
    extension=${filename##*.}
    if [ $extension == "txp" ]; then
        echo $f
        sh temprel-pipeline-per-file.sh $f $2
    fi
done
