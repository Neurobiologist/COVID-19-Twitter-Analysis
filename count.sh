#!/usr/bin/bash

DATA="/projectnb/caad/meganmp/COVID-19-TweetIDs-master/"

cd $DATA

for f in *; do
    if [ -d "$f" ]; then
        echo $f
        cd $f
        for x in *.jsonl.gz
        do
            echo $x #>> /projectnb/caad/meganmp/analysis/count-data.txt
            unpigz -c $x | wc -l >> /projectnb/caad/meganmp/analysis/count-data.txt
            echo >> /projectnb/caad/meganmp/analysis/count-data.txt
        done
        cd $DATA
    fi
done
