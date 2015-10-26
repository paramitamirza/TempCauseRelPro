###########################################################
#Test
###########################################################

#sh temprel-pipeline.sh [dir_txp] [1-step or 2-step] --> 1-step without binary classification, 2-step with binary classification
sh temprel-pipeline.sh ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/ 2-step
sh temprel-pipeline.sh ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/ 2-step
sh temprel-pipeline.sh ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/ 2-step
sh temprel-pipeline.sh ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/ 2-step

#sh causalrel-pipeline.sh [dir_txp] [dir_tlinks]
sh causalrel-pipeline.sh ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/tlinks/
sh causalrel-pipeline.sh ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/tlinks
sh causalrel-pipeline.sh ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/tlinks
sh causalrel-pipeline.sh ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/tlinks

#python mergeLinksTXP.py [dir_txp] [dir_tlinks] [dir_clinks] [dir_output] [-fixtlink] --> -fixtlink is optional, fix TLINK based on CLINK, e.g. e1 CLINK e2 -> e1 BEFORE e2
python mergeLinksTXP.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/tlinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/clinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/tagged/
python mergeLinksTXP.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/tlinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/clinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/tagged/
python mergeLinksTXP.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/tlinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/clinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/tagged/
python mergeLinksTXP.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/tlinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/clinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/tagged/

python mergeLinksTXP.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/tlinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/clinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/fixed/ -fixtlink
python mergeLinksTXP.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/tlinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/clinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/fixed/ -fixtlink
python mergeLinksTXP.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/tlinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/clinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/fixed/ -fixtlink
python mergeLinksTXP.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/tlinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/clinks/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/fixed/ -fixtlink

#python convertTXPtoCAT.py [dir_txp] [dir_output] 
python convertTXPtoCAT.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/tagged/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/tagged-cat/
python convertTXPtoCAT.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/tagged/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/tagged-cat/
python convertTXPtoCAT.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/tagged/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/tagged-cat/
python convertTXPtoCAT.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/tagged/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/tagged-cat/

python convertTXPtoCAT.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/fixed/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_airbus_boeing/fixed-cat/
python convertTXPtoCAT.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/fixed/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_apple/fixed-cat/
python convertTXPtoCAT.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/fixed/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_gm_chrysler_ford/fixed-cat/
python convertTXPtoCAT.py ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/fixed/ ../../data/Wikinews-Relex-NAF-TXP-filtered/corpus_stock_market/fixed-cat/

