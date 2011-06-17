#!/bin/bash -e

BASE_PATH=/home/cronuser/csv-dumps
for db in simple complex
do
    file="$BASE_PATH/$db.csv"
    cat $BASE_PATH/*/*/$db.csv >> "$file.work"
    mv "$file.work" "$file"
done


