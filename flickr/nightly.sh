#!/bin/sh
today=$(date -I)
wget http://flickr.com/creativecommons/ -O "data/$today.html"
python flickr.py < "data/$today.html" > "data/$today.csv"
