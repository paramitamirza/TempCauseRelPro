import sys
import os
import re
import FileFeatures as ff
import subprocess as sp

def __getConceptRel(lemma1, lemma2):
    criteria = {'start':'/c/en/'+lemma1, 'end':'/c/en/'+lemma2}
    assertion = cnetq.query(criteria)
    rel = "O"
    if len(assertion) > 0:
        rel = assertion[0]['rel'][3:]
    return rel

def __getParaphraseCausalSignal(csig, csignal_para_dict):
    csig_para_list = []
    if csig in csignal_para_dict:
        csig_para_list = csignal_para_dict[csig]
    #else:
    #    csig_para_list.append(csig)
    return csig_para_list

def __getParaphraseCausalSignalDict():
    csignal_dict_file = open("causal_signal.dict", "r")
    csignal_para_dict = {}

    for line in csignal_dict_file.readlines():
        cols = line.split("\t")
        csig = cols[0].strip()
        para = cols[1].strip().split("|")
        csignal_para_dict[csig] = para

    csignal_dict_file.close()
    return csignal_para_dict

def getFeatureString(ff, e1, e2, morecs, csignal_para_dict):
    feature_str = ""
    (eidx1, tid1, _, eclass1, _, _) = ff.entities[e1]
    (eidx2, tid2, _, eclass2, _, _) = ff.entities[e2]
    (token1, sentid1, lemma1, pos1, mainvb1, entity1, chunk1, conn1, mainpos1, tense1, aspect1, pol1, supersense1) = ff.tokens[tid1]
    (token2, sentid2, lemma2, pos2, mainvb2, entity2, chunk2, conn2, mainpos2, tense2, aspect2, pol2, supersense2) = ff.tokens[tid2]
    (pos_path1, pos_pol1) = ff.getPOSPath(tid1) #get POS path (for verb, noun and adj are based on dependent verb) and polarity from POS
    (pos_path2, pos_pol2) = ff.getPOSPath(tid2) #get POS path (for verb, noun and adj are based on dependent verb) and polarity from POS
    
    (sent_distance, ent_distance, ent_order) = ff.getDistance(sentid1, sentid2, eidx1, eidx2) 
    if ent_order == "reverse":
        (dep_rel, dep_order) = ff.getDependency(tid2, tid1)
        (dep_path, path_order) = ff.getDependencyPath(tid2, tid1)
    else:
        (dep_rel, dep_order) = ff.getDependency(tid1, tid2)
        (dep_path, path_order) = ff.getDependencyPath(tid1, tid2)
    samePOS = (pos1 == pos2)
    sameClass = (eclass1 == eclass2)
    sameTense = (tense1 == tense2)
    sameAspect = (aspect1 == aspect2)
    samePol = (pol1 == pol2) 
    
    #(marker, marker_position, dep_mark_e1, dep_mark_e2) = (["O"],"O","O","O")
    (marker, marker_position, dep_mark_e1, dep_mark_e2) = ([],"O","O","O")
    if ent_order == "reverse": (causal_signal, causal_signal_pos, dep_signal_e1, dep_signal_e2) = ff.getCausalSignal(e2, e1)
    else: (causal_signal, causal_signal_pos, dep_signal_e1, dep_signal_e2) = ff.getCausalSignal(e1, e2)
    if causal_signal != "O":
        causal_signals = []
        if morecs and ((e1, e2) in ff.clink or (e2, e1) in ff.clink):
            for cs in __getParaphraseCausalSignal(causal_signal, csignal_para_dict):
                causal_signals.append(cs)
        causal_signals.append(causal_signal)
            
        (marker, marker_position, dep_mark_e1, dep_mark_e2) = (causal_signals, causal_signal_pos, dep_signal_e1, dep_signal_e2)
        
    else:
        if ent_order == "reverse": (causal_conn, causal_conn_pos, dep_conn_e1, dep_conn_e2) = ff.getCausalConnective(e2, e1)
        else: (causal_conn, causal_conn_pos, dep_conn_e1, dep_conn_e2) = ff.getCausalConnective(e1, e2)
        if causal_conn != "O":
            causal_conns = []
            causal_conns.append(causal_conn)
            (marker, marker_position, dep_mark_e1, dep_mark_e2) = (causal_conns, causal_conn_pos, dep_conn_e1, dep_conn_e2)
        else:
            if ent_order == "reverse": (causal_verb, dep_e1, dep_e2) = ff.getCausativeVerb(e2, e1)
            else: (causal_verb, dep_e1, dep_e2) = ff.getCausativeVerb(e1, e2)
            if causal_verb != "O":
                causal_verbs = []
                causal_verbs.append(causal_verb)
                (marker, marker_position, dep_mark_e1, dep_mark_e2) = (causal_verbs, "BETWEEN", dep_e1, dep_e2)
                
            
    (csignal_e1, csignal_pos_e1) = ff.getCSignalDependency(e1)
    (csignal_e2, csignal_pos_e2) = ff.getCSignalDependency(e2)
    (cverb_e1, cverb_pos_e1) = ff.getCVerbDependency(e1)
    (cverb_e2, cverb_pos_e2) = ff.getCVerbDependency(e2)
                
    coref = "O"
    if (e1, e2) in ff.coref_events or (e2, e1) in ff.coref_events: coref = "COREF"

    tlink = "O"
    if ent_order == "reverse":
        if (e2, e1) in ff.tlink and ff.tlink[(e2, e1)] != "NONE": tlink = ff.tlink[(e2, e1)]
        elif (e1, e2) in ff.tlink and ff.tlink[(e1, e2)] != "NONE": tlink = ff.getInverseRelation(ff.tlink[(e1, e2)])
        else: tlink = "O"
    else:
        if (e1, e2) in ff.tlink and ff.tlink[(e1, e2)] != "NONE": tlink = ff.tlink[(e1, e2)]
        elif (e2, e1) in ff.tlink and ff.tlink[(e2, e1)] != "NONE": tlink = ff.getInverseRelation(ff.tlink[(e2, e1)])
        else: tlink = "O"
    
    conceptnet = "O"
    #if ent_order == "reverse":
    #    conceptnet = __getConceptRel(lemma2, lemma1)
    #else:
    #    conceptnet = __getConceptRel(lemma1, lemma2)

    pair_str = ""

    feature_strings = ""
    
    for m in marker:
        feature_str = ""
        if ent_order == "reverse":
            feature_str += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
                (e2, e1, token2, token1, lemma2, lemma1, mainpos2+"-"+mainpos1, chunk2+"-"+chunk1, sent_distance, ent_distance, conceptnet, dep_rel, dep_order, dep_path, path_order, str(mainvb2)+"-"+str(mainvb1), eclass2+"-"+eclass1, tense2+"-"+tense1, aspect2+"-"+aspect1, pol2+"-"+pol1, samePOS, sameClass, sameTense, sameAspect, samePol, pos_path2+"-"+pos_path1, pos_pol2+"-"+pos_pol1, m, marker_position, dep_mark_e1, dep_mark_e2, csignal_e2, csignal_pos_e2, csignal_e1, csignal_pos_e1, cverb_e2, cverb_pos_e2, cverb_e1, cverb_pos_e1, tlink, coref, supersense2, supersense1, entity2, entity1)
        else:
            feature_str += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
                (e1, e2, token1, token2, lemma1, lemma2, mainpos1+"-"+mainpos2, chunk1+"-"+chunk2, sent_distance, ent_distance, conceptnet, dep_rel, dep_order, dep_path, path_order, str(mainvb1)+"-"+str(mainvb2), eclass1+"-"+eclass2, tense1+"-"+tense2, aspect1+"-"+aspect2, pol1+"-"+pol2, samePOS, sameClass, sameTense, sameAspect, samePol, pos_path1+"-"+pos_path2, pos_pol1+"-"+pos_pol2, m, marker_position, dep_mark_e1, dep_mark_e2, csignal_e1, csignal_pos_e1, csignal_e2, csignal_pos_e2, cverb_e1, cverb_pos_e1, cverb_e2, cverb_pos_e2, tlink, coref, supersense1, supersense2, entity1, entity2)

        #clink
        clink = "O"
        if ent_order == "reverse":
            if (e2, e1) in ff.clink: clink = "CLINK"
            elif (e1, e2) in ff.clink: clink = "CLINK-R"
            else: clink = "O"
        else:
            if (e1, e2) in ff.clink: clink = "CLINK"
            elif (e2, e1) in ff.clink: clink = "CLINK-R"
            else: clink = "O"

        feature_strings += feature_str + "\t" + clink + "\n"

    return feature_strings
        
def buildPairFeatures(ff, coref, rel, morecs, csignal_para_dict, clink_pairs):
    #print ff.arr_event_ids
    #print ff.clink
    #print ff.entity_array

    feature_str = ""  
    clink = ""
    n = 0
    for ev_sent in ff.arr_event_ids:
        for i in range(len(ev_sent)-1):
            for j in range(i+1, len(ev_sent)):
                #print ev_sent[i], ev_sent[j]
                e1 = ev_sent[i]
                e2 = ev_sent[j]
                if not coref:
                    if (e1, e2) not in ff.coref_events and (e2, e1) not in ff.coref_events:
                        if rel:
                            clink = getFeatureString(ff, e1, e2, morecs, csignal_para_dict).strip().split("\t")[-1]
                            if clink != "O": feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                        else:
                            if clink_pairs:
                                if (e1, e2) in ff.pairs: feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                            else: feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                else: 
                    if rel:
                        clink = getFeatureString(ff, e1, e2, morecs, csignal_para_dict).strip().split("\t")[-1]
                        if clink != "O": feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                    else:
                        if clink_pairs:
                            if (e1, e2) in ff.pairs: feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                        else: feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)

        if n < len(ff.arr_event_ids)-1:
            for i in range(len(ev_sent)):
                for j in range(len(ff.arr_event_ids[n+1])):
                    #print ev_sent[i], ff.arr_event_ids[n+1][j]
                    e1 = ev_sent[i]
                    e2 = ff.arr_event_ids[n+1][j]
                    if not coref:
                        if (e1, e2) not in ff.coref_events and (e2, e1) not in ff.coref_events:
                            if rel:
                                clink = getFeatureString(ff, e1, e2, morecs, csignal_para_dict).strip().split("\t")[-1]
                                if clink != "O": feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                            else:
                                if clink_pairs:
                                    if (e1, e2) in ff.pairs: feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                                else: feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                    else: 
                        if rel:
                            clink = getFeatureString(ff, e1, e2, morecs, csignal_para_dict).strip().split("\t")[-1]
                            if clink != "O": feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                        else:
                            if clink_pairs:
                                if (e1, e2) in ff.pairs: feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)
                            else: feature_str += getFeatureString(ff, e1, e2, morecs, csignal_para_dict)

        n += 1 
        #feature_str += "\n"

    return feature_str

def printUsage():
    print "usage: python buildCRelPairFeatures.py dir_name [options]"
    print "   or: python buildCRelPairFeatures.py file_name [options]"
    print " "                                          
    print "       options   : -s<num> (split), e.g. -s10 for splitting into 10 folds"
    print "                                 splitting will print the pair features into files instead of standard output"
    print "                 : -lang en | it (for language, default: en)"
    print "                 : -inv (for inverse_relation=true)"
    print "                 : -parser stanford | cc | nr (default: stanford, -Stanford CoreNLP or C&C or Newsreader-: differences in lemma, pos, ner, dependency relations)"
    print "                 : -cs  dir_name_csignal | file_name_csignal (for dir_name or file_name of CSIGNALs)"    
    print "                 : -coref  (for co-refer events listed as candidate pairs)"
    print "                 : -rel  (only pairs with CLINK or CLINK-R class)"
    print "                 : -morecs (expand the training data with more causal signals from PDTB)"
    print "                 : -tlink dir_name_tlink | file_name_tlink (for dir_name or file_name of TLINKs)"
    print "                 : -clink dir_name_clink | file_name_clink (for dir_name or file_name of CLINKs)"

#main
if __name__ == '__main__':

    if len(sys.argv) < 2:
        printUsage()
    else:
        split = False
        language = "en"
        parser = "stanford"
        split_size = -99
        inverse = False
        csignal_path = ""
        tlink_path = ""
        tlink_pairs = False
        clink_path = ""        
        clink_pairs = False        
        coref = False
        rel = False
        morecs = False
        if len(sys.argv) > 2:
            options = sys.argv[2:]
            i = 0
            for o in options:
                if len(o) > 2 and o[0:2] == "-s":
                    split = True
                    split_size = int(o[2:])
                if o == "-lang" and i+1<len(options):
                    if options[i+1] in ["en", "it"]: language = options[i+1]
                if o == "-inv":
                    inverse = True
                if o == "-parser" and i+1<len(options):
                    if options[i+1] in ["stanford", "cc", "nr"]: parser = options[i+1]
                if o == "-cs" and i+1<len(options):
                    if os.path.isdir(options[i+1]) or os.path.isfile(options[i+1]): csignal_path = options[i+1]
                if o == "-coref":
                    coref = True
                if o == "-rel":
                    rel = True
                if o == "-morecs":
                    morecs = True
                if o == "-tlink":
                    tlink_pairs = True
                    if os.path.isdir(options[i+1]) or os.path.isfile(options[i+1]): tlink_path = options[i+1]
                if o == "-clink":
                    clink_pairs = True
                    if os.path.isdir(options[i+1]) or os.path.isfile(options[i+1]): clink_path = options[i+1]
                i += 1

        csignal_para_dict = {}
        if morecs == True:
            csignal_para_dict = __getParaphraseCausalSignalDict()
        
        if os.path.isdir(sys.argv[1]):  #input is directory name
            dirpath = sys.argv[1]
            dirpath_csignal = ""
            if csignal_path != "" and os.path.isdir(csignal_path):
                dirpath_csignal = csignal_path

            dirpath_tlink = ""
            if tlink_path != "" and os.path.isdir(tlink_path):
                dirpath_tlink = tlink_path
            
            dirpath_clink = ""
            if clink_path != "" and os.path.isdir(clink_path):
                dirpath_clink = clink_path

            if split == True:
                fout_split = []
                for i in range(split_size):
                    fout_split[i] = open("clink.part" + str(i+1), 'w')

            n = 0
            feature_vectors = ""
            for r, d, f in os.walk(dirpath):
                for filename in f:
                    #print filename
                    #sys.stderr.write(filename + "\n")
                    if filename.endswith(".txp"):
                        filepath = os.path.join(r, filename)
                        input_file = open(filepath, 'r')
                        file_features = ff.FileFeatures(input_file.read(), filename, language, parser, inverse)
                        file_features.getFeatures()
                        if dirpath_csignal != "":
                            filepath_csignal = os.path.join(dirpath_csignal, filename+".csignals")
                            file_csignal = open(filepath_csignal, "r")
                            file_features.initCSignals(file_csignal.read())
                            file_csignal.close()
                        if dirpath_tlink != "":
                            filepath_tlink = os.path.join(dirpath_tlink, filename+".tlinks")
                            file_tlink = open(filepath_tlink, "r")
                            file_features.initTlinkPairs(file_tlink.read())
                            file_tlink.close()
                        if dirpath_clink != "":
                            filepath_clink = os.path.join(dirpath_clink, filename+".clinks")
                            file_clink = open(filepath_clink, "r")
                            file_features.initPairs(file_clink.read())
                            file_clink.close()
                        feature_vectors += buildPairFeatures(file_features, coref, rel, morecs, csignal_para_dict, clink_pairs) + "\n"

                    if split == True:
                        s = n % split_size
                        fout_split[s].write(feature_vectors)
                        feature_vectors = ""

                    n += 1   

                break

            if split == True:
                for fout in fout_split:
                    fout.close()
            else:
                print feature_vectors

        elif os.path.isfile(sys.argv[1]):   #input is file name
            input_file = open(sys.argv[1], 'r')
            
            filename = os.path.basename(sys.argv[1])
            file_features = ff.FileFeatures(input_file.read(), filename, language, parser, inverse)
            file_features.getFeatures()
            if csignal_path != "" and os.path.isfile(csignal_path):
                input_file_csignal = open(csignal_path, 'r')
                file_features.initCSignals(input_file_csignal.read())
                input_file_csignal.close()
            if tlink_path != "" and os.path.isfile(tlink_path):
                input_file_tlink = open(tlink_path, "r")
                file_features.initTlinkPairs(input_file_tlink.read())
                input_file_tlink.close()
            if clink_path != "" and os.path.isfile(clink_path):
                input_file_clink = open(clink_path, "r")
                file_features.initPairs(input_file_clink.read())
                input_file_clink.close()

            feature_vectors = ""
            feature_vectors = buildPairFeatures(file_features, coref, rel, morecs, csignal_para_dict, clink_pairs) + "\n"
            print feature_vectors
        else:
            printUsage()            


        

        
