#!/bin/sh

cd /web/cc/scripts/stats

#Variables.
DIR=/web/teamspace/www/stats
CURRENT=$DIR/daily.xml
LANG=$DIR/lang.xml
DOM=$DIR/domains.xml
ERRLOG=$DIR/link-counts-errors.log
TABBED=$DIR/tabbed.txt
TABBED_HISTORY=$DIR/tabbed_history.txt
DATE=`date +%F`

date >> $ERRLOG

mkdir $DIR/svgs

#Simple beginning--run the new script.
nice /usr/bin/python /web/cc/scripts/stats/link-counts.py 2>> $ERRLOG

#This section appends the new data set to history.
sed '$d' $DIR/history.xml > $DIR/history2.xml
sed '/^$/d' $CURRENT >>$DIR/history2.xml
echo '</Data>' >>$DIR/history2.xml
mv $DIR/history2.xml $DIR/history.xml

#Generate: The tabbed file, the first set of graphs, the second set of graphs, the PNG images, and the executive summaries.
nice /usr/bin/python /web/cc/scripts/stats/tabgen.py > $TABBED 2>> $ERRLOG
nice /usr/bin/python /web/cc/scripts/stats/postprocess.py >> $TABBED  2>> $ERRLOG
cat $TABBED >>$TABBED_HISTORY
nice /usr/bin/python /web/cc/scripts/stats/histgraph.py >> $ERRLOG 2>&1
nice /usr/bin/java -jar /web/cc/scripts/stats/batik/batik-rasterizer.jar $DIR/svgs 2>> $ERRLOG
nice /usr/bin/python /web/cc/scripts/stats/sumgen.py >> $ERRLOG 2>&1


mkdir $DIR/$DATE
mkdir $DIR/$DATE/svgs
mv $DIR/*.htm $DIR/$DATE
mv $DIR/svgs/* $DIR/$DATE/svgs
mv $DIR/daily.xml $DIR/$DATE
mv $DIR/language.xml $DIR/$DATE
mv $DIR/tabbed.txt $DIR/$DATE

rm $DIR/current
ln -s $DIR/$DATE $DIR/current
rmdir $DIR/svgs

nice /usr/bin/python /web/cc/scripts/stats/language.py 2>>$ERRLOG
nice /usr/bin/python /web/cc/scripts/stats/domain.py 2>>$ERRLOG
sed '$d' $DIR/langhist.xml > $DIR/lh2.xml
sed '/^$/d' $LANG >>$DIR/lh2.xml
echo '</Data>' >>$DIR/lh2.xml
mv $DIR/lh2.xml $DIR/langhist.xml

sed '$d' $DIR/domhist.xml > $DIR/dh2.xml
sed '/^$/d' $DOM >>$DIR/dh2.xml
echo '</Data>' >>$DIR/dh2.xml
mv $DIR/dh2.xml $DIR/domhist.xml

gzip -9 $DIR/$DATE/svgs/*.svg
