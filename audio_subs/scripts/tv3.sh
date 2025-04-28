#!/bin/bash

DATA_PATH="/media/clic/ppastells/subs_scrapping_corpus/data/tv3/"

# use --skip-download to avoid the audio files
for file in cuines_Gessami ; do
    filename="/media/clic/ppastells/subs_scrapping_corpus/data/tv3/_indexs/index_$file.txt"

    # loop over the urls in the file
    while IFS= read -r url; do
        id=$(yt-dlp -F "$url" | grep "audio only" | awk '{print $1}')
        yt-dlp --write-subs --sub-langs "ca" -f "$id" "$url"
    done < <(sed 's/3cat.cat/ccma.cat/g' "$filename") # yt-dlp no troba els links de 3cat.cat

    # convert m4a to mp3 with 1 channel and 16kHz
    find . -name "*.m4a" | parallel ffmpeg -i {} -ac 1 -ar 16000 {.}.mp3 -hide_banner \;
    rm ./*.m4a

    # clean
    for f in *.vtt; do
        sed -i -f scripts/clean.sed "$f"
        vtt_to_srt "$f"
        rm "$f"
    done

    mkdir "$DATA_PATH/$file"
    mv ./*.mp3 ./*.srt "$DATA_PATH/$file/"
    # remove unicode characters from name
    (
        cd "$DATA_PATH/$file" || exit
        for f in *; do rename "s/ /_/g" "$f"; done
        for f in *; do rename "s/：/:/g" "$f"; done
        for f in *; do rename "s/｜/|/g" "$f"; done
        for f in *; do rename "s/'//g" "$f"; done
        for f in data/*/*; do rename "s/＂//g" "$f"; done
        for f in data/*/*; do rename "s/？//g" "$f"; done
    )
done
