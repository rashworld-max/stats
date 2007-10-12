#!/bin/sh
today=$(date -I)
wget http://flickr.com/creativecommons/ -O "$today.html"
python flickr.py < "$today.html" > "$today.csv"
