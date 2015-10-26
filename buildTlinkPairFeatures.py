import sys
import os
import FileFeatures as ff

def reverseCLINK(clink):
    if clink == "CLINK": return "CLINK-R"
    elif clink == "CLINK-R": return "CLINK"
        
def buildPairFeatures(ff, pair_type, classification, et_opt, ee_opt):
    event_event_str = ""
    event_timex_str = ""
    timex_timex_str = ""

    event_timex_dct = ""
    event_timex_non_dct = ""
    event_timex_main = ""
    event_event_main = ""

    n_ee_pairs = 0
    n_et_pairs = 0
    n_tt_pairs = 0

    for (e1, e2) in ff.tlink:   
        #print e1, e2, ff.tlink[(e1, e2)]
        if e1 in ff.entities and e2 in ff.entities:     
            if ff.isTimex(e1):
                (eidx1, tid_start1, tid_end1, timex_type1, timex_value1, dct1) = ff.entities[e1]
                if dct1: sentid1 = "O"
                else: (_, sentid1, _, _, _, _, _, _, _, _, _, _, _) = ff.tokens[tid_start1]
                (lemma1, token1) = ff.getLemmaTokenTimex(e1)

                if ff.isTimex(e2):  #timex-timex pair
                    #(eidx2, tid_start2, tid_end2, timex_type2, timex_value2, dct2) = ff.entities[e2]
                    #if dct2: sentid2 = "O"
                    #else: (_, sentid2, _, _, _, _, _, _, _, _, _, _, _) = ff.tokens[tid_start2]
                    #(lemma2, token2) = ff.getLemmaTokenTimex(e2)
                    #(sent_distance, ent_distance, ent_order) = ff.getDistance(sentid1, sentid2, eidx1, eidx2)
                    #(temp_conn1, temp_conn_pos1) = ff.getTemporalConnective(e1)
                    #(temp_conn2, temp_conn_pos2) = ff.getTemporalConnective(e2)
                    #(temp_signal1, temp_signal_pos1) = ff.getTemporalSignal(e1)
                    #(temp_signal2, temp_signal_pos2) = ff.getTemporalSignal(e2)
                    
                    #tt_str = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
                    #    (e1, e2, token1, token2, sent_distance, ent_distance, ent_order, timex_type1+"-"+timex_type2, timex_value1+"-"+timex_value2, dct1, dct2, temp_signal1, temp_signal_pos1, temp_signal2, temp_signal_pos2, temp_conn1, temp_conn_pos1, temp_conn2, temp_conn_pos2)
                    #if classification == "bin":
                    #    if ff.tlink[(e1, e2)] != "NONE": rel_type = "REL"
                    #    else: rel_type = ff.tlink[(e1, e2)]
                    #    timex_timex_str += tt_str + "\t%s\n" % rel_type	
                    #elif classification == "rel":
                    #    if ff.tlink[(e1, e2)] != "NONE": timex_timex_str += tt_str + "\t%s\n" % ff.tlink[(e1, e2)] 
                    #else: timex_timex_str += tt_str + "\t%s\n" % ff.tlink[(e1, e2)]
                    
                    #n_tt_pairs += 1
                    #if n_tt_pairs % 25 == 0: timex_timex_str += "\n"
                    pass
                
                else: #timex-event pair
                    pair_order = "te"
                    (eidx2, tid2, _, eclass2, _, _) = ff.entities[e2]
                    (token2, sentid2, lemma2, pos2, mainvb2, entity2, chunk2, conn2, mainpos2, tense2, aspect2, pol2, supersense2) = ff.tokens[tid2]    
                    (pos_path2, pos_pol2) = ff.getPOSPath(tid2) #get POS path (for verb, noun and adj are based on dependent verb) and polarity from POS
                    
                    (dep_rel, dep_order) = ("O", "O")
                    (dep_path, path_order) = ("O", "O")
                    if not dct1:
                        for i in range(int(tid_start1), int(tid_end1) + 1):
                            (dep_rel, dep_order) = ff.getDependency(tid2, str(i))
                            if dep_rel != "O": break
                            (dep_path, path_order) = ff.getDependencyPath(tid2, str(i))
                            if dep_path != "O": break
                            
                    (sent_distance, ent_distance, ent_order) = ff.getDistance(sentid1, sentid2, eidx1, eidx2)   
                    (temp_conn1, temp_conn_pos1) = ff.getTemporalConnective(e2)
                    (temp_conn2, temp_conn_pos2) = ff.getTemporalConnective(e1)
                    (temp_signal1, temp_signal_pos1) = ff.getTemporalSignal(e2)
                    (temp_signal2, temp_signal_pos2) = ff.getTemporalSignal(e1)  
                    
                    timex_rule = ff.getTimexRule(e1)
                    reltype_rule = ff.getRelTypeRule(temp_signal2, pair_order, eclass2, timex_type1, timex_value1, e1)             
                    
                    et_str = ""
                    et_str += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
                        (e2, e1, pair_order, token2, token1, lemma2, lemma1, mainpos2, chunk2, sent_distance, ent_distance, ent_order, dep_rel, dep_order, dep_path, path_order, mainvb2, eclass2, tense2, aspect2, pol2, timex_type1, timex_value1, dct1, pos_path2, pos_pol2, temp_signal2, temp_signal_pos2, temp_signal1, temp_signal_pos1, temp_conn2, temp_conn_pos2, temp_conn1, temp_conn_pos1, timex_rule)
                    if classification == "bin":
                        if ff.tlink[(e1, e2)] != "NONE": rel_type = "REL"
                        else: rel_type = ff.tlink[(e1, e2)]
                        et_str += "\t%s" % rel_type

                        if et_opt == "dct" and dct1: event_timex_dct += et_str + "\tREL\n"
                        elif et_opt == "non-dct" and not dct1: event_timex_non_dct += et_str + "\tREL\n"
                        elif et_opt == "dct-main" and dct1:
                            if mainvb2: event_timex_dct += et_str + "\tREL\n"
                            else: event_timex_str += et_str + "\n"
                        elif et_opt == "main":
                            if mainvb2: event_timex_main += et_str + "\tREL\n"
                            else: event_timex_str += et_str + "\n"
                        elif et_opt == "rule":
                            if reltype_rule != "O": event_timex_main += et_str + "\t" + reltype_rule + "\n"
                            else: event_timex_str += et_str + "\n"
                        else: event_timex_str += et_str + "\n"
                    elif classification == "rel":
                        if True:
                        #if ff.tlink[(e1, e2)] != "NONE": 
                        #if ff.tlink[(e1, e2)] != "NONE" and ff.tlink[(e1, e2)] != "ENDED_BY" and ff.tlink[(e1, e2)] != "BEGUN_BY":
                        
                            #for QA-TempEval: DURING and IDENTITY are mapped to SIMULTANEOUS, IBEFORE/IAFTER are mapped to BEFORE/AFTER
                            #                 BEGUN_BY, ENDED_BY and INCLUDES are mapped to BEGINS, ENDS and IS_INCLUDED
                            rel_type = ff.getInverseRelation2(ff.tlink[(e1, e2)])
                            #if rel_type == "DURING" or rel_type == "DURING_INV" or rel_type == "IDENTITY": et_str += "\t%s" % "SIMULTANEOUS"
                            if rel_type == "IBEFORE": et_str += "\t%s" % "BEFORE"
                            elif rel_type == "IAFTER": et_str += "\t%s" % "AFTER"
                            elif rel_type == "BEGINS" or rel_type == "ENDS" or rel_type == "INCLUDES": et_str += "\t%s" % ff.getInverseRelation(ff.tlink[(e1, e2)])
                            elif rel_type == "IS_INCLUDED" and timex_type1 == "DURATION": et_str += "\t%s" % "MEASURE"    #for NewsReader
                            else: et_str += "\t%s" % rel_type
                        
                            #et_str += "\t%s" % ff.tlink[(e1, e2)]                            
                            if et_opt == "rule": 
                                if reltype_rule != "O" and sent_distance == 0: event_timex_main += et_str + "\t" + reltype_rule + "\n"
                                else: event_timex_str += et_str + "\n"
                            else: event_timex_str += et_str + "\n"
                    else: event_timex_str += et_str + "\t%s\n" % ff.tlink[(e1, e2)]
                    
                    n_et_pairs += 1
                    #if n_et_pairs % 25 == 0: event_timex_str += "\n"

            else:
                (eidx1, tid1, _, eclass1, _, _) = ff.entities[e1]
                (token1, sentid1, lemma1, pos1, mainvb1, entity1, chunk1, conn1, mainpos1, tense1, aspect1, pol1, supersense1) = ff.tokens[tid1]
                (pos_path1, pos_pol1) = ff.getPOSPath(tid1) #get POS path (for verb, noun and adj are based on dependent verb) and polarity from POS
                
                if ff.isTimex(e2):  #event-timex pair
                    pair_order = "et"
                    (eidx2, tid_start2, tid_end2, timex_type2, timex_value2, dct2) = ff.entities[e2]
                    if dct2: sentid2 = "O"
                    else: (_, sentid2, _, _, _, _, _, _, _, _, _, _, _) = ff.tokens[tid_start2]
                    (lemma2, token2) = ff.getLemmaTokenTimex(e2)
                    
                    (dep_rel, dep_order) = ("O", "O")
                    (dep_path, path_order) = ("O", "O")
                    if not dct2:
                        for i in range(int(tid_start2), int(tid_end2) + 1):
                            (dep_rel, dep_order) = ff.getDependency(tid1, str(i))
                            if dep_rel != "O": break
                            (dep_path, path_order) = ff.getDependencyPath(tid1, str(i))
                            if dep_path != "O": break
                            
                    (sent_distance, ent_distance, ent_order) = ff.getDistance(sentid1, sentid2, eidx1, eidx2)
                    (temp_signal1, temp_signal_pos1) = ff.getTemporalSignal(e1)
                    (temp_signal2, temp_signal_pos2) = ff.getTemporalSignal(e2)
                    (temp_conn1, temp_conn_pos1) = ff.getTemporalConnective(e1)
                    (temp_conn2, temp_conn_pos2) = ff.getTemporalConnective(e2)
                    
                    timex_rule = ff.getTimexRule(e2)
                    reltype_rule = ff.getRelTypeRule(temp_signal2, pair_order, eclass1, timex_type2, timex_value2, e2)      
                    
                    et_str = ""
                    et_str += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
                        (e1, e2, pair_order, token1, token2, lemma1, lemma2, mainpos1, chunk1, sent_distance, ent_distance, ent_order, dep_rel, dep_order, dep_path, path_order, mainvb1, eclass1, tense1, aspect1, pol1, timex_type2, timex_value2, dct2, pos_path1, pos_pol1, temp_signal1, temp_signal_pos1, temp_signal2, temp_signal_pos2, temp_conn1, temp_conn_pos1, temp_conn2, temp_conn_pos2, timex_rule)
                    if classification == "bin":
                        if ff.tlink[(e1, e2)] != "NONE": rel_type = "REL"
                        else: rel_type = ff.tlink[(e1, e2)]
                        et_str += "\t%s" % rel_type

                        if et_opt == "dct" and dct2: event_timex_dct += et_str + "\tREL\n"
                        elif et_opt == "non-dct" and not dct2: event_timex_non_dct += et_str + "\tREL\n"
                        elif et_opt == "dct-main" and dct2:
                            if mainvb1: event_timex_dct += et_str + "\tREL\n"
                            else: event_timex_str += et_str + "\n"
                        elif et_opt == "main":
                            if mainvb1: event_timex_main += et_str + "\tREL\n"
                            else: event_timex_str += et_str + "\n"
                        elif et_opt == "rule":
                            if reltype_rule != "O": event_timex_main += et_str + "\t" + reltype_rule + "\n"
                            else: event_timex_str += et_str + "\n"
                        else: event_timex_str += et_str + "\n"
                    elif classification == "rel":
                        if True:
                        #if ff.tlink[(e1, e2)] != "NONE": 
                        #if ff.tlink[(e1, e2)] != "NONE" and ff.tlink[(e1, e2)] != "ENDED_BY" and ff.tlink[(e1, e2)] != "BEGUN_BY":
                            
                            #for QA-TempEval: DURING and IDENTITY are mapped to SIMULTANEOUS, IBEFORE/IAFTER are mapped to BEFORE/AFTER
                            #                 BEGUN_BY, ENDED_BY and INCLUDES are mapped to BEGINS, ENDS and IS_INCLUDED
                            rel_type = ff.tlink[(e1, e2)]
                            #if rel_type == "DURING" or rel_type == "DURING_INV" or rel_type == "IDENTITY": et_str += "\t%s" % "SIMULTANEOUS"
                            if rel_type == "IBEFORE": et_str += "\t%s" % "BEFORE"
                            elif rel_type == "IAFTER": et_str += "\t%s" % "AFTER"
                            elif rel_type == "BEGINS" or rel_type == "ENDS" or rel_type == "INCLUDES": et_str += "\t%s" % ff.getInverseRelation(ff.tlink[(e1, e2)])
                            elif rel_type == "IS_INCLUDED" and timex_type2 == "DURATION": et_str += "\t%s" % "MEASURE"    #for NewsReader
                            else: et_str += "\t%s" % rel_type
                            
                            #et_str += "\t%s" % ff.tlink[(e1, e2)]                            
                            if et_opt == "rule": 
                                if reltype_rule != "O" and sent_distance == 0: event_timex_main += et_str + "\t" + reltype_rule + "\n"
                                else: event_timex_str += et_str + "\n"
                            else: event_timex_str += et_str + "\n"
                    else: event_timex_str += et_str + "\t%s\n" % ff.tlink[(e1, e2)]   
                    
                    n_et_pairs += 1
                    #if n_et_pairs % 25 == 0: event_timex_str += "\n"                 
                
                else: #event-event pair
                    (eidx2, tid2, _, eclass2, _, _) = ff.entities[e2]
                    (token2, sentid2, lemma2, pos2, mainvb2, entity2, chunk2, conn2, mainpos2, tense2, aspect2, pol2, supersense2) = ff.tokens[tid2] 
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
                    (temp_conn1, temp_conn_pos1) = ff.getTemporalConnective(e1)
                    (temp_conn2, temp_conn_pos2) = ff.getTemporalConnective(e2)
                    (temp_signal1, temp_signal_pos1) = ff.getTemporalSignal(e1)
                    (temp_signal2, temp_signal_pos2) = ff.getTemporalSignal(e2)                      
                    
                    if ent_order == "reverse":
                        if (e2, e1) in ff.clink: clink = ff.clink[(e2, e1)]
                        else: clink = "O"
                    else:
                        if (e1, e2) in ff.clink: clink = ff.clink[(e1, e2)]
                        else: clink = "O"
                        
                    coref = "O"
                    if (e1, e2) in ff.coref_events or (e2, e1) in ff.coref_events: coref = "COREF"
                    
                    ee_str = ""                   
                    if ent_order == "reverse":
                        ee_str += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
                            (e2, e1, token2, token1, lemma2, lemma1, mainpos2+"-"+mainpos1, chunk2+"-"+chunk1, sent_distance, ent_distance, ent_order, dep_rel, dep_order, dep_path, path_order, str(mainvb2)+"-"+str(mainvb1), eclass2+"-"+eclass1, tense2+"-"+tense1, aspect2+"-"+aspect1, pol2+"-"+pol1, samePOS, sameClass, sameTense, sameAspect, samePol, pos_path2+"-"+pos_path1, pos_pol2+"-"+pos_pol1, temp_signal2, temp_signal_pos2, temp_signal1, temp_signal_pos1, temp_conn2, temp_conn_pos2, temp_conn1, temp_conn_pos1, clink, coref)
                    else:
                        ee_str += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
                            (e1, e2, token1, token2, lemma1, lemma2, mainpos1+"-"+mainpos2, chunk1+"-"+chunk2, sent_distance, ent_distance, ent_order, dep_rel, dep_order, dep_path, path_order, str(mainvb1)+"-"+str(mainvb2), eclass1+"-"+eclass2, tense1+"-"+tense2, aspect1+"-"+aspect2, pol1+"-"+pol2, samePOS, sameClass, sameTense, sameAspect, samePol, pos_path1+"-"+pos_path2, pos_pol1+"-"+pos_pol2, temp_signal1, temp_signal_pos1, temp_signal2, temp_signal_pos2, temp_conn1, temp_conn_pos1, temp_conn2, temp_conn_pos2, clink, coref)
                    if classification == "bin":
                        if ff.tlink[(e1, e2)] != "NONE": rel_type = "REL"
                        else: rel_type = ff.tlink[(e1, e2)]
                        ee_str += "\t%s" % rel_type
                        
                        if ee_opt == "main":
                            if mainvb1 or mainvb2: event_event_main += ee_str + "\tREL\n"
                            else: event_event_str += ee_str + "\n"
                        elif ee_opt == "coref":
                            if coref == "COREF": event_event_main += ee_str + "\tSIMULTANEOUS\n"    #NewsReader and QA-TempEval no IDENTITY
                            #if coref == "COREF": event_event_main += ee_str + "\tIDENTITY\n"
                            else: event_event_str += ee_str + "\n"
                        else: event_event_str += ee_str + "\n"

                    elif classification == "rel":
                        if True:
                        #if ff.tlink[(e1, e2)] != "NONE": 
                        #if ff.tlink[(e1, e2)] != "NONE" and ff.tlink[(e1, e2)] != "BEGINS" and ff.tlink[(e1, e2)] != "BEGUN_BY" and ff.tlink[(e1, e2)] != "ENDS" and ff.tlink[(e1, e2)] != "ENDED_BY" and ff.tlink[(e1, e2)] != "IAFTER" and ff.tlink[(e1, e2)] != "IBEFORE": 
                            
                            #for QA-TempEval: DURING and IDENTITY are mapped to SIMULTANEOUS, IBEFORE/IAFTER are mapped to BEFORE/AFTER
                            rel_type = ff.tlink[(e1, e2)]
                            if ent_order == "reverse": rel_type = ff.getInverseRelation2(rel_type)
                            #if rel_type == "DURING" or rel_type == "DURING_INV" or rel_type == "IDENTITY": ee_str += "\t%s" % "SIMULTANEOUS"
                            if rel_type == "IBEFORE": ee_str += "\t%s" % "BEFORE"
                            elif rel_type == "IAFTER": ee_str += "\t%s" % "AFTER"
                            else: ee_str += "\t%s" % rel_type  
                            
                            #event_event_str += ee_str + "\t%s\n" % ff.tlink[(e1, e2)]
                            
                            if ee_opt == "coref":
                                if coref == "COREF": event_event_main += ee_str + "\tSIMULTANEOUS\n"	#NewsReader and QA-TempEval no IDENTITY
                                #if coref == "COREF": event_event_main += ee_str + "\tIDENTITY\n"
                                else: event_event_str += ee_str + "\n"
                            else: event_event_str += ee_str + "\n"
                        
                    else: event_event_str += ee_str + "\t%s\n" % ff.tlink[(e1, e2)]
                    
                    n_ee_pairs += 1
                    #if n_ee_pairs % 25 == 0: event_event_str += "\n"  
                    
    for (e1, e2) in ff.tmxlink:
        timex_timex_str += e1 + "\t" + e2 + "\t" + ff.tmxlink[(e1, e2)] + "\n"

    #print event_event_str    
    #print event_timex_str
    #print timex_timex_str

    if pair_type == "ee": 
        if ee_opt == "main": return (event_event_main, event_event_str)
        elif ee_opt == "coref": 
            #the rest of the corefer-events not in tlinks? label them as SIMULTANEOUS?
            for (coev1, coev2) in ff.coref_events:
                if (coev1, coev2) not in ff.tlink and (coev2, coev1) not in ff.tlink:
                    print coev1 + "\t" + coev2 + "\tSIMULTANEOUS"        #NewsReader and QA-TempEval no IDENTITY
                    #print coev1 + "\t" + coev2 + "\tIDENTITY"                        
            return (event_event_main, event_event_str)
        else: return event_event_str
    elif pair_type == "et": 
        if et_opt == "dct": return (event_timex_dct, event_timex_str)
        elif et_opt == "non-dct": return (event_timex_non_dct, event_timex_str)
        elif et_opt == "dct-main": return (event_timex_dct, event_timex_str)
        elif et_opt == "main": return (event_timex_main, event_timex_str)
        elif et_opt == "rule": return (event_timex_main, event_timex_str)
        else: return event_timex_str
    elif pair_type == "tt": return timex_timex_str

def printUsage():
    print "usage: python buildTempRelPairFeatures.py dir_name pair_type [options]"
    print "   or: python buildTempRelPairFeatures.py file_name pair_type [options]"
    print " "                                          
    print "       pair_type : ee (event-event pair) | et (event-timex pair) | tt (timex-timex pair)"
    print "       options   : -s<num> (split), e.g. -s10 for splitting into 10 folds"
    print "                                 splitting will print the pair features into ype = files instead of standard output"
    print "                 : -type bin | rel (for type of classification, binary classification [REL or NONE] or relation type classification [NONE type is ignored)]"
    print "                 : -et dct | non-dct | dct-main | main | rule (for event-timex pairs, which one is considered as having REL, the rest are to be classified)"
    print "                 : -ee main | coref (for event-timex pairs, which one is considered as having REL, the rest are to be classified)"
    print "                                 this will also print the pair features into files instead of standard output"
    print "                 : -lang en | it (for language, default: en)"
    print "                 : -inv (for inverse_relation=true)"
    print "                 : -parser stanford | cc | nr (default: stanford, -Stanford CoreNLP or C&C or Newsreader-: differences in lemma, pos, ner, dependency relations)"

#main
if __name__ == '__main__':

    if len(sys.argv) < 3:
        printUsage()
    else:
        split = False
        classification = ""
        language = "en"
        parser = "stanford"
        et_opt = ""
        ee_opt = ""
        split_size = -99
        inverse = False
        if len(sys.argv) > 3:
            options = sys.argv[3:]
            i = 0
            for o in options:
                if len(o) > 2 and o[0:2] == "-s":
                    split = True
                    split_size = int(o[2:])
                if o == "-type" and i+1<len(options):
                    if options[i+1] in ["bin", "rel"]: classification = options[i+1]
                if o == "-et" and i+1<len(options):
                    if options[i+1] in ["dct", "non-dct", "dct-main", "main", "rule"]: et_opt = options[i+1]
                if o == "-ee" and i+1<len(options):
                    if options[i+1] in ["main", "coref"]: ee_opt = options[i+1]
                if o == "-lang" and i+1<len(options):
                    if options[i+1] in ["en", "it"]: language = options[i+1]
                if o == "-inv":
                    inverse = True
                if o == "-parser" and i+1<len(options):
                    if options[i+1] in ["stanford", "cc", "nr"]: parser = options[i+1]
                i += 1
        
        pair_type = sys.argv[2]
        if pair_type == "ee" or pair_type == "et" or pair_type == "tt":

            if os.path.isdir(sys.argv[1]):  #input is directory name
                dirpath = sys.argv[1]

                count = 0
                for r, d, f in os.walk(dirpath):
                    for file in f:
                        if file.endswith('.txp') or file.endswith('.col'): count += 1
                #print count

                n = 1
                s = 0
                feature_vectors = ""
                feature_vectors_rel = ""
                feature_vectors_none = ""
                feature_vectors_dct_none = ""
                for r, d, f in os.walk(dirpath):
                    for filename in f:
                        #print filename
                        if split == True:
                            maxn = count/split_size
                            if s < (count%split_size): maxn += 1 
                            if n == maxn * (s+1):
                                fout_split = open(pair_type + ".part" + str(s+1), 'w')
                                fout_split.write(feature_vectors)
                                fout_split.close()
                                feature_vectors = ""
                                s += 1
                        if filename.endswith(".txp") or filename.endswith(".col"):
                            filepath = os.path.join(r, filename)
                            input_file = open(filepath, 'r')
                            file_features = ff.FileFeatures(input_file.read(), filename, language, parser, inverse)
                            file_features.getFeatures()
                            if et_opt != "" or ee_opt != "":
                                (pairs0, pairs1) = buildPairFeatures(file_features, pair_type, classification, et_opt, ee_opt)
                                if pairs0 != "": feature_vectors_rel += pairs0 + "\n"
                                if pairs1 != "": feature_vectors_none += pairs1 + "\n"
                            else:
                                pairs = buildPairFeatures(file_features, pair_type, classification, et_opt, ee_opt)
                                if pairs != "": feature_vectors += pairs + "\n"
                        n += 1   
                        
                (file_rel, file_none, file_dct_none) = ("", "", "")
                if classification == "bin" and (et_opt != "" or ee_opt != ""):
                    if et_opt == "dct": 
                        file_rel = ".dct.rel"
                        file_none = ".non.dct.none"
                    elif et_opt == "non-dct":
                        file_rel = ".non.dct.rel"
                        file_none = ".dct.none"
                    elif et_opt == "dct-main":
                        file_rel = ".dct.main.rel"
                        file_none = ".dct.non.dct.none"
                    elif et_opt == "main":
                        file_rel = ".main.rel"
                        file_none = ".non.main.none"
                    elif et_opt == "rule":
                        file_rel = ".rule.rel"
                        file_none = ".non.rule.none" 
                    elif ee_opt == "main":
                        file_rel = ".main.rel"
                        file_none = ".non.main.none"
                    elif ee_opt == "coref":
                        file_rel = ".coref.rel"
                        file_none = ".non.coref.none"
                elif classification == "rel" and (et_opt != "" or ee_opt != ""):
                    if et_opt == "rule":
                        file_rel = ".rule.rel"
                        file_none = ".non.rule.none"
                    elif ee_opt == "coref":
                        file_rel = ".coref.rel"
                        file_none = ".non.coref.none"

                if et_opt != "" or ee_opt != "":
                    fout_rel = open(pair_type + file_rel + ".tlinks", 'w')
                    fout_rel.write(feature_vectors_rel)
                    fout_rel.close()

                    fout_none = open(pair_type + file_none + ".tlinks", 'w')                    
                    fout_none.write(feature_vectors_none)
                    fout_none.close()

                else:
                    print feature_vectors
                    #print "...done"

            elif os.path.isfile(sys.argv[1]):   #input is file name
                input_file = open(sys.argv[1], 'r')
                filename = os.path.basename(sys.argv[1])
                file_features = ff.FileFeatures(input_file.read(), filename, language, parser, inverse)
                file_features.getFeatures()

                feature_vectors = ""
                feature_vectors_rel = ""
                feature_vectors_none = ""
                feature_vectors_dct_none = ""

                if et_opt != "" or ee_opt != "":
                    (pairs0, pairs1) = buildPairFeatures(file_features, pair_type, classification, et_opt, ee_opt)
                    if pairs0 != "": feature_vectors_rel = pairs0 + "\n"
                    if pairs1 != "": feature_vectors_none = pairs1 + "\n"
                else:
                    pairs = buildPairFeatures(file_features, pair_type, classification, et_opt, ee_opt)
                    if pairs != "": feature_vectors = pairs + "\n"

                if classification == "bin" and (et_opt != "" or ee_opt != ""):
                    if et_opt == "dct": 
                        file_rel = ".dct.rel"
                        file_none = ".non.dct.none"
                    elif et_opt == "non-dct":
                        file_rel = ".non.dct.rel"
                        file_none = ".dct.none"
                    elif et_opt == "dct-main":
                        file_rel = ".dct.main.rel"
                        file_none = ".dct.non.dct.none"
                    elif et_opt == "main":
                        file_rel = ".main.rel"
                        file_none = ".non.main.none"
                    elif ee_opt == "main":
                        file_rel = ".main.rel"
                        file_none = ".non.main.none"
                    elif et_opt == "rule":
                        file_rel = ".rule.rel"
                        file_none = ".non.rule.none" 
                    elif ee_opt == "coref":
                        file_rel = ".coref.rel"
                        file_none = ".non.coref.none"
                elif classification == "rel" and (et_opt != "" or ee_opt != ""):
                    if et_opt == "rule":
                        file_rel = ".rule.rel"
                        file_none = ".non.rule.none" 
                    elif ee_opt == "coref":
                        file_rel = ".coref.rel"
                        file_none = ".non.coref.none"

                if et_opt != "" or ee_opt != "":
                    fout_rel = open(filename + "." + pair_type + file_rel, 'w')
                    fout_rel.write(feature_vectors_rel)
                    fout_rel.close()

                    fout_none = open(filename + "." + pair_type + file_none, 'w')                    
                    fout_none.write(feature_vectors_none)
                    fout_none.close()
                else:
                    print feature_vectors
            else:
                print "File/directory " + sys.argv[1] + " doesn't exist."
        else:
            printUsage()            


        

        
