#!/usr/bin/bash

DATA="/projectnb/caad/meganmp/data/usa-tweets/"

cd $DATA

for f in *; do
    if [ -d "$f" ]; then
        echo $f >> /projectnb/caad/meganmp/analysis/results/characterization/usa-tweets/count-data.txt
        cd $f
        for x in *.jsonl.gz
        do
            unpigz -c $x | wc -l >> /projectnb/caad/meganmp/analysis/results/characterization/usa-tweets/count-data.txt
            echo >> /projectnb/caad/meganmp/analysis/results/characterization/usa-tweets/count-data.txt
        done
        cd $DATA
    fi
done
