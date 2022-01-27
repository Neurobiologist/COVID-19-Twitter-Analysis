#!/usr/bin/bash

DATA="/data/usa-tweets/"

cd $DATA

for f in *; do
    if [ -d "$f" ]; then
        echo $f >> /analysis/results/characterization/usa-tweets/count-data.txt
        cd $f
        for x in *.jsonl.gz
        do
            unpigz -c $x | wc -l >> /analysis/results/characterization/usa-tweets/count-data.txt
            echo >> /analysis/results/characterization/usa-tweets/count-data.txt
        done
        cd $DATA
    fi
done
