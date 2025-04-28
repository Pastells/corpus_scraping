#!/bin/bash

DATA_PATH="/media/clic/ppastells/subs_scrapping_corpus/data/tv3"
CORPUS_PATH="/media/clic/ppastells/subs_scrapping_corpus/corpus_tv3/"

for file in "$DATA_PATH"/cuines_Gessami/; do
# for file in "$DATA_PATH"/*/; do
    echo "$file"
    find "$file" -type f -name "*.mp3" | parallel -j 4 \
        python3 utils/srt-audio-split.py {} {.}.ca.srt \
        --output-dir "$CORPUS_PATH/$(basename $file)" \;
done

(
    cd  $CORPUS_PATH || exit
    rm  -f all.csv
    awk 'FNR==1 && NR!=1{next;}{print}' ./*/*.csv > all.csv
)
