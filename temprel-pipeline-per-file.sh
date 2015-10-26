#!/bin/sh
filename=$(basename "$1")
#filename="${filename%%.*}"
if [ ! -d "`dirname $1`/tlinks/" ]; then
    mkdir `dirname $1`/tlinks/
fi

yamcha="../../../Dropbox/PhDStuff/Event_Relation/tools/fbk/yamcha-0.33/usr/local/bin/yamcha"

if [ "$2" == "1-step" ]; then
    python buildTlinkPairFeatures.py $1 tt > `dirname $1`/$filename.tt
    python buildTlinkPairFeatures.py $1 ee -type rel -ee coref -lang en -parser nr > `dirname $1`/$filename.ee.coref
    python buildTlinkPairFeatures.py $1 et -type rel -et rule -lang en -parser nr

    $yamcha -V -m ./models/tlink-rel-ee.model < $filename.ee.non.coref.none > $filename.ee.non.coref.none.tagged
    cat $filename.ee.non.coref.none.tagged $filename.ee.coref.rel > `dirname $1`/tlinks/$filename.ee.tagged

    $yamcha -V -m ./models/tlink-rel-et.model < $filename.et.non.rule.none > $filename.et.non.rule.none.tagged
    cat $filename.et.non.rule.none.tagged $filename.et.rule.rel > `dirname $1`/tlinks/$filename.et.tagged

    rm $filename.ee.non.coref.none $filename.ee.non.coref.none.tagged $filename.ee.coref.rel
    rm $filename.et.non.rule.none $filename.et.non.rule.none.tagged $filename.et.rule.rel

    cut -f1,2,39- `dirname $1`/tlinks/$filename.ee.tagged > `dirname $1`/tlinks/$filename.ee.verbose
    python orderTlinks.py `dirname $1`/tlinks/$filename.ee.verbose > `dirname $1`/tlinks/$filename.ee
    cat `dirname $1`/$filename.ee.coref >> `dirname $1`/tlinks/$filename.ee     #labelling the rest of co-refer pairs (not listed as candidate pairs) as SIMULTANEOUS

    cut -f1,2,37- `dirname $1`/tlinks/$filename.et.tagged > `dirname $1`/tlinks/$filename.et.verbose
    python orderTlinks.py `dirname $1`/tlinks/$filename.et.verbose > `dirname $1`/tlinks/$filename.et

    cat `dirname $1`/$filename.tt `dirname $1`/tlinks/$filename.ee `dirname $1`/tlinks/$filename.et | grep . > `dirname $1`/tlinks/$filename.tlinks

    rm `dirname $1`/tlinks/$filename.ee.tagged `dirname $1`/tlinks/$filename.et.tagged
    rm `dirname $1`/tlinks/$filename.ee.verbose `dirname $1`/tlinks/$filename.et.verbose
    rm `dirname $1`/$filename.tt `dirname $1`/tlinks/$filename.ee `dirname $1`/tlinks/$filename.et

    rm `dirname $1`/$filename.ee.coref

elif [ "$2" == "2-step" ]; then
    python buildTlinkPairFeatures.py $1 tt > `dirname $1`/$filename.tt
    
    python buildTlinkPairFeatures.py $1 ee -type bin -ee coref -lang en -parser nr > `dirname $1`/$filename.ee.coref
    $yamcha -m ./models/tlink-bin-ee.model < $filename.ee.non.coref.none > $filename.ee.bin.tagged

    python buildTlinkPairFeatures.py $1 et -type rel -et rule -lang en -parser nr
    $yamcha -m ./models/tlink-bin-et.model < $filename.et.non.rule.none > $filename.et.bin.tagged

    awk -F"\t" '$39=="REL" || NF==0 { print; }' $filename.ee.bin.tagged | cut -f-37,39 > $filename.ee.non.coref.none
    $yamcha -V -m ./models/tlink-rel-ee.model < $filename.ee.non.coref.none > $filename.ee.non.coref.none.tagged
    cat $filename.ee.non.coref.none.tagged $filename.ee.coref.rel > `dirname $1`/tlinks/$filename.ee.tagged

    awk -F"\t" '$37=="REL" || NF==0 { print; }' $filename.et.bin.tagged | cut -f-35,37  > $filename.et.non.rule.none
    $yamcha -V -m ./models/tlink-rel-et.model < $filename.et.non.rule.none > $filename.et.non.rule.none.tagged
    cat $filename.et.non.rule.none.tagged $filename.et.rule.rel > `dirname $1`/tlinks/$filename.et.tagged

    rm $filename.ee.bin.tagged $filename.et.bin.tagged
    rm $filename.ee.non.coref.none $filename.ee.non.coref.none.tagged $filename.ee.coref.rel
    rm $filename.et.non.rule.none $filename.et.non.rule.none.tagged $filename.et.rule.rel

    cut -f1,2,39- `dirname $1`/tlinks/$filename.ee.tagged > `dirname $1`/tlinks/$filename.ee.verbose
    python orderTlinks.py `dirname $1`/tlinks/$filename.ee.verbose > `dirname $1`/tlinks/$filename.ee
    cat `dirname $1`/$filename.ee.coref >> `dirname $1`/tlinks/$filename.ee     #labelling the rest of co-refer pairs (not listed as candidate pairs) as SIMULTANEOUS

    cut -f1,2,37- `dirname $1`/tlinks/$filename.et.tagged > `dirname $1`/tlinks/$filename.et.verbose
    python orderTlinks.py `dirname $1`/tlinks/$filename.et.verbose > `dirname $1`/tlinks/$filename.et

    cat `dirname $1`/$filename.tt `dirname $1`/tlinks/$filename.ee `dirname $1`/tlinks/$filename.et | grep . > `dirname $1`/tlinks/$filename.tlinks

    rm `dirname $1`/tlinks/$filename.ee.tagged `dirname $1`/tlinks/$filename.et.tagged
    rm `dirname $1`/tlinks/$filename.ee.verbose `dirname $1`/tlinks/$filename.et.verbose
    rm `dirname $1`/$filename.tt `dirname $1`/tlinks/$filename.ee `dirname $1`/tlinks/$filename.et

    rm `dirname $1`/$filename.ee.coref
fi
