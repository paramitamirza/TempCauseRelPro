###########################################################
#Build pair feature
###########################################################

#TLINKs
python buildTlinkPairFeatures.py ../../data/RelEx_QATempEval_train/ ee -type bin -lang en -parser nr > train-temp-bin-ee.tlinks
python buildTlinkPairFeatures.py ../../data/RelEx_QATempEval_train/ et -type bin -lang en -parser nr > train-temp-bin-et.tlinks

python buildTlinkPairFeatures.py ../../data/RelEx_QATempEval_train/ ee -type rel -lang en -parser nr > train-temp-rel-ee.tlinks
python buildTlinkPairFeatures.py ../../data/RelEx_QATempEval_train/ et -type rel -lang en -parser nr > train-temp-rel-et.tlinks

#CLINKs
python buildClinkPairFeatures.py ../../data/Causal-TimeBank-NAF-TXP/ -lang en -parser nr -coref > train-causal-timebank.clinks

###########################################################
#Train
###########################################################
cd ~/Dropbox/PhDStuff/Event_Relation/tools/fbk/yamcha-0.33/

#TLINKs

make CORPUS=~/CauseRel_virtual/tools/TempCauseRelPro/train-temp-bin-ee.tlinks MODEL=~/CauseRel_virtual/tools/TempCauseRelPro/models/tlink-bin-ee FEATURE="F:0:2,3,4,5,6,7,8,9,11,13,14,15,17,18,19,20,22,23,25,26,27,28,29,30,31,32,33,34,36" SVM_PARAM="-t1 -d2 -c1 -m 512" train
make CORPUS=~/CauseRel_virtual/tools/TempCauseRelPro/train-temp-bin-et.tlinks MODEL=~/CauseRel_virtual/tools/TempCauseRelPro/models/tlink-bin-et FEATURE="F:0:3,4,5,6,7,8,9,10,11,12,14,17,18,19,21,23,24,25,26,27,28,29,34" SVM_PARAM="-t1 -d2 -c1 -m 512" train

make CORPUS=~/CauseRel_virtual/tools/TempCauseRelPro/train-temp-rel-ee.tlinks MODEL=~/CauseRel_virtual/tools/TempCauseRelPro/models/tlink-rel-ee FEATURE="F:0:2,3,4,5,6,7,8,9,11,13,14,15,17,18,19,20,22,23,25,26,27,28,29,30,31,32,33,34" SVM_PARAM="-t1 -d2 -c1 -m 512" train
make CORPUS=~/CauseRel_virtual/tools/TempCauseRelPro/train-temp-rel-et.tlinks MODEL=~/CauseRel_virtual/tools/TempCauseRelPro/models/tlink-rel-et FEATURE="F:0:3,4,5,6,7,8,9,10,11,12,14,17,18,19,21,23,24,25,26,27,28,29" SVM_PARAM="-t1 -d2 -c1 -m 512" train

#CLINKs
make CORPUS=~/CauseRel_virtual/tools/TempCauseRelPro/train-causal-timebank.clinks MULTI_CLASS=2 MODEL=~/CauseRel_virtual/tools/TempCauseRelPro/models/clink FEATURE="F:0:4,5,6,7,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23,24,25,26,27,28,29,30,39,40" SVM_PARAM="-t1 -d2 -c1 -m 512" train

