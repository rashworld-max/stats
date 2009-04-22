#!/bin/bash -e
# Today's estimate
cd /home/paulproteus/stats/reports
python nightly_ml_calculator.py --mode one

# Update the world!
cd /home/paulproteus/public_html/stats/ml-minimum-estimate/
for engine in 2009-01-24/*; do
    engine=${engine/2009-01-24\//}
    engine=${engine/.txt/}
    TEMPFILE=$(mktemp -p . cumulative.csv.XXXXXXXX)
    cat */"$engine.txt" | grep TOTAL > "$TEMPFILE"
    chmod 644 "$TEMPFILE"
    mv "$TEMPFILE" "$engine.cumulative.csv"
done
