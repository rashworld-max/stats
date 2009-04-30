#!/bin/sh
today=$(date -I)
right_now=$(date "+%s")
wget -q http://flickr.com/creativecommons/ -O "data/$today.html" || \
    (echo "wget failed!  Why?" ; exit 1)
python flickr.py --unix-time=$right_now < "data/$today.html"
