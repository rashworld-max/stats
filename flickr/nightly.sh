#!/bin/sh
today=$(date -I)
wget -q http://flickr.com/creativecommons/ -O "data/$today.html" || \
    (echo "wget failed!  Why?" ; exit 1)
python flickr.py < "data/$today.html" > "data/$today.csv"
