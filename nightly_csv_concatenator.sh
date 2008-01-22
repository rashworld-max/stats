#!/bin/bash -xe

BASE_PATH=/home/paulproteus/csv-dumps
for db in simple complex
do
    file="$BASE_PATH/$db.csv"
    find "$BASE_PATH"  -iname simple.csv | xargs cat >> "$file.work"
    mv "$file.work" "$file"
done


