#!/bin/sh
filename=$(basename "$1")
#filename="${filename%%.*}"
if [ ! -d "`dirname $1`/clinks/" ]; then
    mkdir `dirname $1`/clinks/
fi

yamcha="../../../Dropbox/PhDStuff/Event_Relation/tools/fbk/yamcha-0.33/usr/local/bin/yamcha"

python buildClinkPairFeatures.py $1 -lang en -parser nr -coref -tlink $2/$filename.tlinks > `dirname $1`/$filename.cl

#$yamcha -V -m ./models/$2.model < `dirname $1`/$filename.cl | cut -f1,2,47- > `dirname $1`/clinks/$filename.verbose
#cat `dirname $1`/clinks/$filename.verbose | cut -f1,2,3  | awk -F"\t" '$3=="CLINK" || $3=="CLINK-R" { print ; }' > `dirname $1`/clinks/$filename.clinks

$yamcha -m ./models/clink.model < `dirname $1`/$filename.cl | cut -f1,2,47 | awk -F"\t" '$3=="CLINK" || $3=="CLINK-R" { print ; }' > `dirname $1`/clinks/$filename.clinks

rm `dirname $1`/$filename.cl
