#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys

class FileFeatures:
    def __init__(self, content, filename, language="en", parser="stanford", inverse=False):
        self.filename = filename
        self.content = content
        self.lang = language
        self.parser = parser
        self.inverse = inverse
        
        self.dependencies = {}
        self.tokens = {}
        self.tokens_extra = {}
        self.tokens_csignal = {}
        self.sentences_start = []
        self.sentences_end = []
        self.entities = {}
        self.entity_array = []
        self.tlink = {}
        self.clink = {}
        self.tmxlink = {}

        self.pairs = {}
        
        self.coref_events = {}

        self.arr_tokens = []
        self.arr_events = {}
        self.arr_timex_starts = {}
        self.arr_timex_ends = {}
        
        self.arr_event_ids = []
        
        self.csignals = {}
        self.arr_csignal_starts = {}
        self.arr_csignal_ends = {}

        self.token_id = 0
        self.sent_id = 0
        self.entity_idx = 0
        self.entity_id = ""
        (self.timex_startid, self.timex_endid, self.tmx_type, self.tmx_value) = ("", "", "", "")
        self.timex_start = False
        
        (self.csignal_startid, self.csignal_endid) = ("", "")
        self.csignal_start = False
        
        #for EVENTI
        self.eventi_task = "C" # task C or D
        
        self.periphrastic_cause_verbs = ["bribe", "cause", "compel", "convince", "drive", "have", "impel", "incite", "induce", "influence", "inspire", "lead", "move", "persuade", "prompt", "push", "force", "get", "make", "rouse", "send", "set", "spur", "start", "stimulate", "entail", "generate", "trigger", "inflict", "result", "provoke"]
        self.periphrastic_enable_verbs = ["aid", "allow", "enable", "help", "leave", "let", "permit", "empower", "facilitate", "afford", "provide", "activate", "authorize", "authorise"]
        self.periphrastic_prevent_verbs = ["bar", "block", "constrain", "deter", "discourage", "dissuade", "hamper", "hinder", "hold", "impede", "keep", "prevent", "protect", "restrain", "restrict", "save", "stop", "deny", "obstruct", "inhibit", "prohibit", "forestall", "impede", "avert", "avoid", "preclude"]
        self.affect_verbs = ["affect", "influence", "determine", "change", "impact", "afflict", "undermine", "alter", "interfere"]
        self.link_verbs = ["link", "lead", "depend", "result"]

        

    def __parseTenseAspectPol(self, tense_aspect_pol):
        if tense_aspect_pol != "O" and tense_aspect_pol != "_" :
            tap = tense_aspect_pol.rstrip().split('+')
            return (tap[0], tap[1], tap[2])
        else:
            return ("O", "O", "O")

    def __parseDependency(self, tokenid, dep):
        if dep != "O":
            for d in dep.rstrip().split('||'):
                dependent = d.split(':')
                tokendep = dependent[0]
                deprel = dependent[1]
                if tokendep[0] == "t": tokendep = tokendep[1:]	#english corpus: tokenid = t1, italian corpus: tokenid = 1
                if tokenid not in self.dependencies: self.dependencies[tokenid] = {}
                self.dependencies[tokenid][tokendep] = deprel

    def __getFieldValue(self, fieldname, cols):
        if self.lang == "it":
            #different fields for Italian-EVENTI
            if self.eventi_task == "C": #task C
                fields = ["token", "token_id", "sent_id", "pos", "lemma", "dep_rel", "tmx_id", "tmx_type", "tmx_value", "entity", "ev_class", "ev_id", "sem_role1", "sem_role2", "sem_role3", "is_arg_pred", "has_semrole", "chunk", "main_verb", "connective", "comp_morpho", "morpho_pos", "ev_tense+ev_aspect+ev_pol", "tlink"]

            elif self.eventi_task == "D": #task D
                fields = ["token", "token_id", "sent_id", "pos", "lemma", "dep_rel", "tmx_id", "tmx_type", "tmx_value", "entity", "ev_class", "ev_id", "sem_role1", "sem_role2", "sem_role3", "is_arg_pred", "has_semrole", "chunk", "main_verb", "connective", "comp_morpho", "morpho_pos", "ev_tense", "ev_aspect", "ev_pol", "tlink"]
            
        else:   #default: en
            #RelEx-QA-Tempeval: token, token_id, sent_id, nr_pos, nr_lemma, nr_deps, tmx_id, tmx_type, tmx_value, nr_ner, ev_class, ev_id, role1, role2, role3, is_arg_pred, has_semrole, nr_chunk, nr_main_verb, nr_connective, nr_morpho, ev_tense+ev_aspect+ev_pol, nr_coevent, tlink
            #fields = ["token", "token_id", "sent_id", "nr_pos", "nr_lemma", "nr_deps", "tmx_id", "tmx_type", "tmx_value", "nr_ner", "ev_class", "ev_id", "role1", "role2", "role3", "is_arg_pred", "has_semrole", "nr_chunk", "nr_main_verb", "nr_connective", "nr_morpho", "ev_tense+ev_aspect+ev_pol", "nr_coevent", "tlink"]
            
            #Stanford: st_lemma, st_pos, st_ner, st_basicdeps, st_collapseddeps, main_verb
            #C&C: cc_lemma, cc_pos, chunk, cc_ner, cc_deps
            #AddDiscourse: connective
            #fields = ["token", "token_id", "sent_id", "nr_pos", "nr_lemma", "nr_deps", "tmx_id", "tmx_type", "tmx_value", "nr_ner", "ev_class", "ev_id", "role1", "role2", "role3", "is_arg_pred", "has_semrole", "nr_chunk", "nr_main_verb", "nr_connective", "nr_morpho", "ev_tense+ev_aspect+ev_pol", "nr_coevent", "tlink", "st_lemma", "st_pos", "st_ner", "st_basicdeps", "st_collapseddeps", "main_verb", "cc_lemma", "cc_pos", "chunk", "cc_ner", "cc_deps", "connective"]
         
            #RelEx + Causality
            fields = ["token", "token_id", "sent_id", "nr_pos", "nr_lemma", "nr_deps", "tmx_id", "tmx_type", "tmx_value", "nr_ner", "ev_class", "ev_id", "role1", "role2", "role3", "is_arg_pred", "has_semrole", "nr_chunk", "nr_main_verb", "nr_connective", "nr_morpho", "ev_tense+ev_aspect+ev_pol", "nr_coevent", "tlink", "clink", "csig_id"]
                
        if fieldname in fields:
            if fields.index(fieldname) < len(cols): return cols[fields.index(fieldname)]
            else: return "O"
        else: return "O" 
        
    def __getMainPos(self, pos):
        if pos == "CC": mainpos = "conj"
        elif pos[0:2] == "CJ": mainpos = "conj"
        elif pos == "CD": mainpos = "num"
        elif pos == "CRD": mainpos = "num"
        elif pos == "ORD": mainpos = "num"
        elif pos == "DT": mainpos = "det"
        elif pos[0:2] == "AT": mainpos = "det"
        elif pos[0] == "D": mainpos = "det"
        elif pos == "EX": mainpos = "ext"
        elif pos[0:2] == "EX": mainpos = "ext"
        elif pos == "FW": mainpos = "foreign"
        elif pos == "UNC": mainpos = "foreign"
        elif pos == "IN": mainpos = "prep"
        elif pos[0:2] == "PR": mainpos = "prep"
        elif pos[0] == "J": mainpos = "adj"
        elif pos[0:2] == "AJ": mainpos = "adj"
        elif pos == "LS": mainpos = "list"
        elif pos == "MD": mainpos = "mod"
        elif pos[0] == "N": mainpos = "noun"
        elif pos == "PDT": mainpos = "predet"
        elif pos == "POS": mainpos = "pos"
        elif pos[0:2] == "PR": mainpos = "pronoun"
        elif pos[0:2] == "PN": mainpos = "pronoun"
        elif pos[0:2] == "RB": mainpos = "adv"
        elif pos[0:2] == "AV": mainpos = "adv"
        elif pos == "RP": mainpos = "part"
        elif pos == "SYM": mainpos = "sym"
        elif pos == "TO": mainpos = "to"
        elif pos[0:2] == "TO": mainpos = "to"
        elif pos == "UH": mainpos = "uh"
        elif pos == "ITJ": mainpos = "uh"
        elif pos[0] == "V": mainpos = "verb"
        elif pos[0] == "W": mainpos = "wh"
        elif pos[0:2] == "PU": mainpos = "punct"
        else: mainpos = "O"
        return pos + "-" + mainpos
        
    def __getMainPosFromMorpho(self, morpho):
        if morpho != "":
            morphs = morpho.split("+")
            if len(morphs) == 1: return morphs[0]
            else: return morphs[1]
        else:
            return "O"

    def parseLine(self, line):
        cols = line.rstrip().split('\t')
        
        #token, tokenid, sentid
        token = self.__getFieldValue("token", cols)
        token = token.replace("°", "")  #doesn't work for  training by Yamcha
        tokenid = self.__getFieldValue("token_id", cols)
        if tokenid[0] == "t": tokenid = tokenid[1:]	#english corpus: tokenid = t1, italian corpus: tokenid = 1
        self.tokenid = tokenid
        sentid = self.__getFieldValue("sent_id", cols)
        if self.sent_id != sentid and sentid != "O" and sentid != "-99":
            self.sentences_start.append(tokenid)
            self.sent_id = sentid
            if tokenid != "O":
                if int(tokenid) > 1:
                    self.sentences_end.append(str(int(tokenid)-1))

        #entity features
        eventid = self.__getFieldValue("ev_id", cols)        
        eventclass = self.__getFieldValue("ev_class", cols)
        if "-" in eventclass: eventclass = eventclass[2:] #english corpus: eventclass = B-...
        timexid = self.__getFieldValue("tmx_id", cols)
        timextype = self.__getFieldValue("tmx_type", cols)
        if "-" in timextype: timextype = timextype[2:]
        timexvalue = self.__getFieldValue("tmx_value", cols)
        
        #csignal
        csignalid = self.__getFieldValue("csig_id", cols)

        if token[0:3] == "DCT" or token[0:3] == "ETX":     #dct or empty token (for italian corpus)
            self.entities[timexid] = (self.entity_idx, tokenid, tokenid, timextype, timexvalue, True)
            self.entity_array.append(timexid)
            self.entity_idx += 1
        else:                       #token
            #token features
            if self.lang == "it":
                pos = self.__getFieldValue("pos", cols)
                lemma = self.__getFieldValue("lemma", cols)
                lemma = lemma.replace("°", "") #doesn't work for training with Yamcha
                entity = self.__getFieldValue("entity", cols)
            else: #default: en
                if self.parser == "stanford":
                    pos = self.__getFieldValue("st_pos", cols)
                    lemma = self.__getFieldValue("st_lemma", cols)
                    entity = self.__getFieldValue("st_ner", cols)
                elif self.parser == "cc":
                    pos = self.__getFieldValue("cc_pos", cols)
                    lemma = self.__getFieldValue("cc_lemma", cols)
                    entity = self.__getFieldValue("cc_ner", cols)
                elif self.parser == "nr":
                    pos = self.__getFieldValue("nr_pos", cols)
                    lemma = self.__getFieldValue("nr_lemma", cols)
                    entity = self.__getFieldValue("nr_ner", cols)
            
            if self.parser == "nr":
                chunk = self.__getFieldValue("nr_chunk", cols)
            else:
                chunk = self.__getFieldValue("chunk", cols)
                
            supersense = "O"
                
            mainstr = self.__getFieldValue("main_verb", cols)
            if self.parser == "nr": mainstr = self.__getFieldValue("nr_main_verb", cols)
            if mainstr == "mainVb": mainvb = True
            else: mainvb = False
            #conn = self.__getFieldValue("connective", cols)
            conn = self.__getFieldValue("nr_connective", cols)
            
            if self.lang == "it":
                mainpos = self.__getFieldValue("morpho_pos", cols)   #doesn't exist for English
            else: #default: en
                if self.parser == "stanford" or self.parser == "cc":
                    mainpos = self.__getMainPos(pos)
                else:   #nr
                    mainpos = self.__getMainPosFromMorpho(self.__getFieldValue("nr_morpho", cols))

            #dependency features
            dep_rel = "O"
            if self.lang == "it":
                self.__parseDependency(tokenid, self.__getFieldValue("dep_rel", cols))
            else: #default: en
                if self.parser == "stanford":
                    dep_rel = self.__getFieldValue("st_basicdeps", cols)
                    self.__parseDependency(tokenid, self.__getFieldValue("st_basicdeps", cols))
                elif self.parser == "cc":
                    dep_rel = self.__getFieldValue("cc_deps", cols)
                    self.__parseDependency(tokenid, self.__getFieldValue("cc_deps", cols))
                elif self.parser == "nr":
                    dep_rel = self.__getFieldValue("nr_deps", cols)
                    self.__parseDependency(tokenid, self.__getFieldValue("nr_deps", cols))
            
            #tense, aspect, polarity
            if self.lang == "it":
                if self.eventi_task == "C": #task C
                    (tense, aspect, pol) = self.__parseTenseAspectPol(self.__getFieldValue("ev_tense+ev_aspect+ev_pol", cols))          
                elif self.eventi_task == "D": #task D
                    (tense, aspect, pol) = (self.__getFieldValue("ev_tense", cols), self.__getFieldValue("ev_aspect", cols), self.__getFieldValue("ev_pol", cols))
            else: #default: en
                #(tense, aspect, pol) = (self.__getFieldValue("ev_tense", cols), self.__getFieldValue("ev_aspect", cols), self.__getFieldValue("ev_pol", cols))
                (tense, aspect, pol) = self.__parseTenseAspectPol(self.__getFieldValue("ev_tense+ev_aspect+ev_pol", cols))
            
            self.tokens[tokenid] = (token, sentid, lemma, pos, mainvb, entity, chunk, conn, mainpos, tense, aspect, pol, supersense)
            self.tokens_extra[tokenid] = (dep_rel, eventid, timexid, csignalid)
            self.arr_tokens.append(tokenid)

            #event
            if eventid != "O":
                self.entities[eventid] = (self.entity_idx, tokenid, tokenid, eventclass, "O", False)
                self.arr_events[tokenid] = eventid
                self.entity_array.append(eventid)
                self.entity_idx += 1
                
                while len(self.arr_event_ids) < int(sentid): self.arr_event_ids.append([])
                self.arr_event_ids[int(sentid)-1].append(eventid)
                
                #event co-reference
                if self.__getFieldValue("nr_coevent", cols) != "O":
                    coevents = self.__getFieldValue("nr_coevent", cols).split(":")
                    for coev in coevents:
                        if (coev, eventid) not in self.coref_events:
                            self.coref_events[(eventid, coev)] = True

            #timex
            if self.entity_id == "" and timexid != "O" and eventid == "O":
                self.entity_id = timexid
                (self.timex_startid, self.timex_endid, self.tmx_type, self.tmx_value) = (tokenid, tokenid, timextype, timexvalue)
            elif self.entity_id == timexid:
                self.timex_endid = tokenid
            elif self.entity_id != timexid and self.timex_startid != "" and self.timex_endid != "":
                self.entities[self.entity_id] = (self.entity_idx, self.timex_startid, self.timex_endid, self.tmx_type, self.tmx_value, False)
                self.entity_array.append(self.entity_id)
                self.arr_timex_starts[self.timex_startid] = self.entity_id
                self.arr_timex_ends[self.timex_endid] = self.entity_id
                self.entity_idx += 1
                self.entity_id = ""
                (self.timex_startid, self.timex_endid, self.tmx_type, self.tmx_value) = ("", "", "", "")
                
            #csignal
            if self.entity_id == "" and csignalid != "O" and eventid == "O" and timexid == "O":
                self.entity_id = csignalid
                (self.csignal_startid, self.csignal_endid) = (tokenid, tokenid)
            elif self.entity_id == csignalid:
                self.csignal_endid = tokenid
            elif self.entity_id != csignalid and self.csignal_startid != "" and self.csignal_endid != "":
                #self.entities[self.entity_id] = (self.entity_idx, self.csignal_startid, self.csignal_endid, "O", "O", False)
                #self.entity_array.append(self.entity_id)
                self.csignals[self.entity_id] = (self.entity_idx, self.csignal_startid, self.csignal_endid, "O", "O", False)
                self.arr_csignal_starts[self.csignal_startid] = self.entity_id
                self.arr_csignal_ends[self.csignal_endid] = self.entity_id
                #self.entity_idx += 1
                self.entity_id = ""
                (self.csignal_startid, self.csignal_endid) = ("", "")
                
        #entity pairs
        if eventid != "O" or timexid != "O":
            #tlink
            relations = self.__getFieldValue("tlink", cols)
            if relations.rstrip() != "O" and relations.rstrip() != "_NULL_":
                rels = relations.rstrip().split('||')
                for rel in rels:
                    strrel = rel.split(':')
                    if len(strrel) == 3:
                        (source, target, reltype) = (strrel[0], strrel[1], strrel[2])
                        if reltype != "": self.tlink[source, target] = reltype
                    
                        #inverse relations
                        reltype_inverse = self.getInverseRelation(reltype)
                        if self.inverse == True and reltype_inverse != None:
                            self.tlink[target, source] = reltype_inverse
                        
            #clink
            relations = self.__getFieldValue("clink", cols)
            if relations.rstrip() != "O" and relations.rstrip() != "_NULL_":
                rels = relations.rstrip().split('||')
                for rel in rels:
                    strrel = rel.split(':')
                    if len(strrel) >= 2:
                        (source, target) = (strrel[0], strrel[1])
                        self.clink[(source, target)] = "CLINK"
                    
                        #inverse relations
                        if self.inverse == True: self.clink[(target, source)] = "CLINK-R"
                        
            #tmxlink
            self.getTimexRel()

    def __findTemporalConnective(self, sid, tidx_start, tidx_end):
        temp_conn = "O"
        temp_position = "O"

        for i in xrange(tidx_start, tidx_end, -1):
            if sid == self.tokens[str(i)][1]:
                if self.tokens[str(i)][7] == "Temporal":
                    temp_conn = self.tokens[str(i)][2]			#lemma
                    #temp_conn = self.tokens[str(i)][0].lower()	#token.lower()
                    temp_position = "BEFORE"
            else:
                break

        return (temp_conn, temp_position)
        
    def __findCausalConnective(self, sid, tidx_start, tidx_end):
        causal_conn = "O"
        cconn_position = "O"
        cconn_id = "O"

        for i in xrange(tidx_start, tidx_end-1, -1):
            if sid == self.tokens[str(i)][1]:
                if self.tokens[str(i)][7] == "Contingency":
                    causal_conn = self.tokens[str(i)][2]			#lemma
                    #causal_conn = self.tokens[str(i)][0].lower()	#token.lower()
                    cconn_position = "BEFORE"
                    cconn_id = str(i)
            else:
                break

        return (causal_conn, cconn_position, cconn_id)

    def isDCT(self, entity_id):
        return self.entities[entity_id][-1]

    def getTemporalConnective(self, entity_id):
        temp_conn = "O"
        temp_position = "O"

        if not self.isDCT(entity_id):
            (eidx, tid, _, _, _, _) = self.entities[entity_id]
            tidx = int(tid)
            sid = self.tokens[tid][1]
            
            tid_begin = self.sentences_start[int(sid)-1]
            tidx_begin = int(tid_begin)

            if eidx > 1:    #because eidx 0 is always DCT
                eid_before = self.entity_array[eidx-1]
                (_, _, tid_before, _, _, _) = self.entities[eid_before]
                if tid_before != "O":
                    tidx_before = int(tid_before)
                    (temp_conn, temp_position) = self.__findTemporalConnective(sid, tidx-1, tidx_before)
                
            else:    
                (temp_conn, temp_position) = self.__findTemporalConnective(sid, tidx-1, tidx_begin-1)

            if temp_position == "O":
                if self.tokens[tid_begin][7] == "Temporal":
                    temp_conn = self.tokens[tid_begin][2]
                    temp_position = "BEGIN"

        return (temp_conn, temp_position)
        
    def getCausalConnective(self, eid1, eid2):
        causal_conn = "O"
        causal_position = "O"
        cconn_id = "O"

        (sent_idx1, eidx1) = (0, "")
        (sent_idx2, eidx2) = (0, "")
        for a in self.arr_event_ids:
            if eid1 in a:
                sent_idx1 = self.arr_event_ids.index(a)
                eidx1 = a.index(eid1)
            if eid2 in a:
                sent_idx2 = self.arr_event_ids.index(a)
                eidx2 = a.index(eid2)
        #print entity_id, sent_idx, eidx
        
        (_, tid1, _, _, _, _) = self.entities[eid1]
        tidx1 = int(tid1)
        (_, tid2, _, _, _, _) = self.entities[eid2]
        tidx2 = int(tid2)

        if sent_idx1 == sent_idx2 and eidx1 != "" and eidx2 != "":
            #if eidx2-3 >= 0:  eid_before = self.arr_event_ids[sent_idx1][eidx2-3]
            #elif eidx2-2 >= 0:  eid_before = self.arr_event_ids[sent_idx1][eidx2-2]
            #else: eid_before = self.arr_event_ids[sent_idx1][eidx2-1]
            eid_before = self.arr_event_ids[sent_idx1][eidx2-1]
            (_, _, tid_before, _, _, _) = self.entities[eid_before]
            tidx_before = int(tid_before)
            (causal_conn, causal_position, cconn_id) = self.__findCausalConnective(str(sent_idx1+1), tidx2-1, tidx_before+1)
            if causal_conn == "O":
                if eidx1 > 0:
                    #eid_before = self.arr_event_ids[sent_idx1][eidx1-3]
                    eid_before = self.arr_event_ids[sent_idx1][eidx1-1]
                    (_, _, tid_before, _, _, _) = self.entities[eid_before]
                    tidx_before = int(tid_before)
                    
                    (causal_conn, causal_position, cconn_id) = self.__findCausalConnective(str(sent_idx1+1), tidx1-1, tidx_before+1)
                    if causal_conn != "O" and causal_position != "O": causal_position = "BEFORE"
                else:
                    tid_begin = self.sentences_start[sent_idx1]
                    tidx_begin = int(tid_begin)                
                    (causal_conn, causal_position, cconn_id) = self.__findCausalConnective(str(sent_idx1+1), tidx1-1, tidx_begin)
                    if causal_conn != "O" and causal_position != "O": causal_position = "BEGIN"  

        elif sent_idx1 != sent_idx2 and eidx1 != "" and eidx2 != "":
            #print eidx1, self.tokens[tid1][2], str(sent_idx1+1), eidx2, self.tokens[tid2][2], str(sent_idx2+1)
            tid_begin = self.sentences_start[sent_idx2]
            tidx_begin = int(tid_begin)
            eid_after = self.arr_event_ids[sent_idx2][0]
            (_, _, tid_after, _, _, _) = self.entities[eid_after]
            tidx_after = int(tid_after)            
            (causal_conn, causal_position, cconn_id) = self.__findCausalConnective(str(sent_idx2+1), tidx_after-1, tidx_begin)
            if causal_conn != "O" and causal_position != "O": causal_position = "BEGIN-BETWEEN"
            else:
                tid_begin = self.sentences_start[sent_idx1]
                tidx_begin = int(tid_begin)
                eid_after = self.arr_event_ids[sent_idx1][0]
                (_, _, tid_after, _, _, _) = self.entities[eid_after]
                tidx_after = int(tid_after)   
                (causal_conn, causal_position, cconn_id) = self.__findCausalConnective(str(sent_idx1+1), tidx_after-1, tidx_begin)
                if causal_conn != "O" and causal_position != "O": causal_position = "BEGIN-BEFORE"

        (dep_e1, dep_e2) = ("O", "O")
        if causal_conn != "O" and cconn_id != "O":
            (_, tid1, _, _, _, _) = self.entities[eid1]
            (_, tid2, _, _, _, _) = self.entities[eid2] 
        
            (dep_e1, _) = self.getDependencyPath(cconn_id, tid1)           
            (dep_e2, _) = self.getDependencyPath(cconn_id, tid2)
            
        return (causal_conn, causal_position, dep_e1, dep_e2)
        
    def __findCausalSignal(self, sid, tidx_start, tidx_end):
        causal_signal = "O"
        csig_position = "O"
        csig_tid_arr = []
            
        csignals = [x.strip() for x in open("causal_signal.list", "r").readlines()]

        context = " "
        for i in xrange(tidx_end, tidx_start+1):
            if sid == self.tokens[str(i)][1]:
                #context += self.tokens[str(i)][2] + " "            #lemma as context for finding signals
                context += self.tokens[str(i)][0].lower() + " "     #token.lower() as context for finding signals
            else:
                break
              
        for cs in csignals:
            (csig, csig_cluster) = cs.split(" ||| ")
            if re.search(" " + csig + " ", context) is not None:
                #print "--", csig, "#", context
                causal_signal = csig_cluster.replace(" ", "-")
                csig_position = "BETWEEN"
                csig_start = csig.strip().split(" ")[0]
                for j in xrange(tidx_end, tidx_start):
                    if csig_start == self.tokens[str(j)][2]: csig_tid_arr.append(str(j))
                break;

        return (causal_signal, csig_position, csig_tid_arr)
        
    def __findCausalSignalOld(self, sid, tidx_start, tidx_end):
        causal_signal_arr = []
        csig_position = "O"
        csig_tid_arr = []

        if self.tokens_csignal:
            dict_csignal = self.tokens_csignal
        else:
            dict_csignal = self.tokens_extra    

        for i in xrange(tidx_start, tidx_end-1, -1):
            if sid == self.tokens[str(i)][1]:
                if dict_csignal[str(i)][3] != "O":
                    causal_signal_arr.append(self.tokens[str(i)][2])			#lemma
                    csig_position = "BETWEEN"
                    csig_tid_arr.append(str(i))
            else:
                break

        if causal_signal_arr != []: causal_signal = "-".join(reversed(causal_signal_arr))
        else: causal_signal = "O"
        
        if csig_tid_arr != []: csig_tid_arr = csig_tid_arr[::-1]

        return (causal_signal, csig_position, csig_tid_arr)
        
    def __findCausalVerb(self, sid, tidx_start, tidx_end):
        causal_verb = "O"
        cverb_id = "O"
        found = False

        for i in xrange(tidx_start, tidx_end-1, -1):
            if sid == self.tokens[str(i)][1] and not found:
                if self.tokens[str(i)][2] in self.periphrastic_cause_verbs and self.tokens[str(i)][8][0] == "v":
                    causal_verb = "CAUSE"
                    cverb_id = str(i)
                    found = True
                elif self.tokens[str(i)][2] in self.periphrastic_enable_verbs and self.tokens[str(i)][8][0] == "v":
                    causal_verb = "ENABLE"
                    cverb_id = str(i)
                    found = True
                elif self.tokens[str(i)][2] in self.periphrastic_prevent_verbs and self.tokens[str(i)][8][0] == "v":
                    causal_verb = "PREVENT"
                    cverb_id = str(i)
                    found = True
                elif self.tokens[str(i)][2] in self.affect_verbs and self.tokens[str(i)][8][0] == "v":
                    causal_verb = "AFFECT"
                    cverb_id = str(i)
                    found = True
                elif self.tokens[str(i)][2] in self.link_verbs and self.tokens[str(i)][8][0] == "v" and self.tokens[str(i+1)][2] in ["to", "in", "on", "with"]:
                    causal_verb = "LINK"
                    cverb_id = str(i)
                    found = True
            else:
                break

        return (causal_verb, cverb_id)

    def isTimex(self, entity_id):
        if entity_id[0:3] == "tmx":
            return True
        else:
            return False

    def __getContextSignal(self, sid, tidx_start, tidx_end):
        context = []
        for i in xrange(tidx_start, tidx_end, -1):
            if sid == self.tokens[str(i)][1]:
                #context.append(self.tokens[str(i)][2])				#lemma as context for finding signals
                context.append(self.tokens[str(i)][0].lower())		#token.lower() as context for finding signals
            else:
                break
        context.reverse()
        return context
        
    def getTimexRule(self, entity_id):
        #For QA-TempEval: add new feature for timespan timexes, e.g. "between" tmx1 "and" tmx2, "from" tmx1 "to" tmx 2, tmx1 "-" tmx2, tmx1 "until" tmx2
        #                 we said that timex is "TMX-BEGIN" or "TMX-END"
        if self.isTimex(entity_id) and not self.isDCT(entity_id):
            (eidx, tid_start, tid_end, _, _, _) = self.entities[entity_id]
            tidx_start = int(tid_start)
            tidx_end = int(tid_end)
            sid = self.tokens[str(tidx_start)][1]
            tidx_begin = int(self.sentences_start[int(sid)-1])
            tidx_last = int(self.sentences_end[int(sid)-1])
            if tidx_start > tidx_begin and tidx_start < tidx_last:
                if eidx < len(self.entity_array)-1 and self.isTimex(self.entity_array[eidx+1]):
                    if self.tokens[str(tidx_start-1)][2] == "between" and self.tokens[str(tidx_end+1)][2] == "and":
                        return "TMX-BEGIN"
                    elif self.tokens[str(tidx_start-1)][2] == "from" and (self.tokens[str(tidx_end+1)][2] == "to" or self.tokens[str(tidx_end+1)][2] == "until" or self.tokens[str(tidx_end+1)][2] == "till"):
                        return "TMX-BEGIN"
                    elif self.tokens[str(tidx_end+1)][2] == "-":
                        return "TMX-BEGIN"
                    elif self.tokens[str(tidx_end+1)][2] == "until" or self.tokens[str(tidx_end+1)][2] == "till":
                        return "TMX-BEGIN"
                elif eidx > 1 and self.isTimex(self.entity_array[eidx-1]):
                    eid_before = self.entity_array[eidx-1]
                    (_, _, tid_before, _, _, _) = self.entities[eid_before]
                    tidx_before = int(tid_before)
                    if self.tokens[str(tidx_start-1)][2] == "and" and self.tokens[str(tidx_before-1)][2] == "between":
                        return "TMX-END"
                    elif (self.tokens[str(tidx_start-1)][2] == "to" or self.tokens[str(tidx_start-1)][2] == "until" or self.tokens[str(tidx_start-1)][2] == "till") and self.tokens[str(tidx_before-1)][2] == "from":
                        return "TMX-END"
                    elif self.tokens[str(tidx_end-1)][2] == "-":
                        return "TMX-END"
                    elif self.tokens[str(tidx_end-1)][2] == "until" or self.tokens[str(tidx_end-1)][2] == "till":
                        return "TMX-END"
        return "O"

    def getTemporalSignal(self, entity_id):
        temp_signal = "O"
        temp_position = "O"
        
        if self.lang == "it":
            #different signal files for italian
            signal_time_filename = "it-signal-timex-lemma.list"
            signal_event_filename = "it-signal-event-lemma.list"
        else:	#default: en
            signal_time_filename = "signal-timex.list"
            signal_event_filename = "signal-event.list"
            
        if not self.isDCT(entity_id):
            (eidx, tid_start, tid_end, _, _, _) = self.entities[entity_id]
            tidx_start = int(tid_start)
            tidx_end = int(tid_end)
            sid = self.tokens[tid_start][1]
            
            tid_begin = self.sentences_start[int(sid)-1]
            tid_last = self.sentences_end[int(sid)-1]
            tidx_begin = int(tid_begin)
            tidx_last = int(tid_last)
            
            context_before = ""
            if eidx > 1:    #because eidx 0 is always DCT
                eid_before = self.entity_array[eidx-1]
                (_, _, tid_before, _, _, _) = self.entities[eid_before]
                if tid_before != "O":
                    tidx_before = int(tid_before)
                    context_before = " ".join(self.__getContextSignal(sid, tidx_start-1, tidx_before))
            else:   
                context_before = " ".join(self.__getContextSignal(sid, tidx_start-1, tidx_begin-1))
                
            context_after = ""
            if eidx < len(self.entity_array)-1:    #before the last entity
                eid_after = self.entity_array[eidx+1]
                (_, tid_after, _, _, _, _) = self.entities[eid_after]
                if tid_after != "O":
                    tidx_after = int(tid_after)
                    context_after = " ".join(self.__getContextSignal(sid, tidx_after-1, tidx_end))
            else:   
                context_after = " ".join(self.__getContextSignal(sid, tidx_last, tidx_end))
                
            if self.isTimex(entity_id):
                signals = [x.strip() for x in open(signal_time_filename, "r").readlines()]
                
                #sometimes the signal is within the timex itself
                (lemma, _) = self.getLemmaTokenTimex(entity_id)
                timex_lemma = lemma.replace("_", " ") + " "
                for signal in signals:
                    if " "+signal+" " in timex_lemma or (signal+" " in timex_lemma and timex_lemma.index(signal) == 0) or (signal+" " in timex_lemma and len(signal+" ") == len(timex_lemma)):
                        sig_tokens = signal.split(" ")
                        temp_signal = "-".join(sig_tokens)
                        if timex_lemma.index(signal) == 0: temp_position = "BEFORE"
                        else: temp_position = "AFTER"
                        return (temp_signal, temp_position)
                
                for signal in signals:
                    if " " + signal + " " in context_before or (signal + " " in context_before and context_before.index(signal) == 0) or (signal in context_before and len(signal) == len(context_before)):
                        sig_tokens = signal.split(" ")
                        temp_signal = "-".join(sig_tokens)
                        temp_position = "BEFORE"
                        return (temp_signal, temp_position)
                    elif " " + signal + " " in context_after or (signal + " " in context_after and context_after.index(signal) == 0) or (signal in context_after and len(signal) == len(context_after)):
                        sig_tokens = signal.split(" ")
                        temp_signal = "-".join(sig_tokens)
                        temp_position = "AFTER"
                        return (temp_signal, temp_position)
                
            else:
                signals = [x.strip() for x in open(signal_event_filename, "r").readlines()]
                
                for signal in signals:
                    if " " + signal + " " in context_before or (signal + " " in context_before and context_before.index(signal) == 0) or (signal in context_before and len(signal) == len(context_before)):
                        sig_tokens = signal.split(" ")
                        temp_signal = "-".join(sig_tokens)
                        temp_position = "BEFORE"

                if temp_position == "O":
                    if self.lang == "it":
                        context_before = " ".join(self.__getContextSignal(sid, tidx_begin+2, tidx_begin-1))
                    else:	#default: en
                        if tidx_begin+4 <= int(tid_last):
                            context_before = " ".join(self.__getContextSignal(sid, tidx_begin+4, tidx_begin-1))
                        else:
                            context_before = " ".join(self.__getContextSignal(sid, tidx_last, tidx_begin-1))
                    for signal in signals:
                        if signal + " " in context_before and context_before.index(signal) == 0:
                            sig_tokens = signal.split(" ")
                            temp_signal = "-".join(sig_tokens)
                            temp_position = "BEGIN"

        return (temp_signal, temp_position)
        
    def getCausativeVerb(self, eid1, eid2):
        (causal_verb, cverb_id) = ("O", "O")

        (sent_idx1, eidx1) = (0, "")
        (sent_idx2, eidx2) = (0, "")
        for a in self.arr_event_ids:
            if eid1 in a:
                sent_idx1 = self.arr_event_ids.index(a)
                eidx1 = a.index(eid1)
            if eid2 in a:
                sent_idx2 = self.arr_event_ids.index(a)
                eidx2 = a.index(eid2)
        #print entity_id, sent_idx, eidx

        if sent_idx1 == sent_idx2 and eidx1 != "" and eidx2 != "":
            (_, tid1, _, _, _, _) = self.entities[eid1]
            tidx1 = int(tid1)
            (_, tid2, _, _, _, _) = self.entities[eid2]
            tidx2 = int(tid2)

            #eid_before = self.arr_event_ids[sent_idx1][eidx2-1]
            #(_, _, tid_before, _, _, _) = self.entities[eid_before]
            #tidx_before = int(tid_before)

            #(causal_verb, cverb_id) = self.__findCausalVerb(str(sent_idx1+1), tidx2-1, tidx_before+1)
            (causal_verb, cverb_id) = self.__findCausalVerb(str(sent_idx1+1), tidx2-1, tidx1+1)

        (dep_e1, dep_e2) = ("O", "O")
        if causal_verb != "O" and cverb_id != "O":
            (_, tid1, _, _, _, _) = self.entities[eid1]
            (_, tid2, _, _, _, _) = self.entities[eid2] 
        
            (dep_e1, _) = self.getDependencyPath(cverb_id, tid1)           
            (dep_e2, _) = self.getDependencyPath(cverb_id, tid2)
        
        return (causal_verb, dep_e1, dep_e2)  
        
    def initCSignals(self, csignal_str):
        for tok in csignal_str.splitlines():
            if tok != "":
                self.tokens_csignal[tok.split("\t")[0]] = ("O", "O", "O", tok.split("\t")[1])

    def initPairs(self, clink_str):
        #self.clink = {}
        for line in clink_str.splitlines():
            if line != "":
                cols = line.strip().split("\t")
                self.pairs[(cols[0], cols[1])] = cols[2]
                if cols[2] == "CLINK":
                    self.clink[(cols[0], cols[1])] = "CLINK"
                elif cols[2] == "CLINK-R":
                    self.clink[(cols[1], cols[0])] = "CLINK"

    def initTlinkPairs(self, tlink_str):
        self.tlink = {}
        for line in tlink_str.splitlines():
            if line != "":
                cols = line.strip().split("\t")
                self.tlink[(cols[0], cols[1])] = cols[2]
        
    def getCausalSignal(self, eid1, eid2):
        causal_signal = "O"
        causal_position = "O"
        csig_tid_arr = []

        (sent_idx1, eidx1) = (0, "")
        (sent_idx2, eidx2) = (0, "")
        for a in self.arr_event_ids:
            if eid1 in a:
                sent_idx1 = self.arr_event_ids.index(a)
                eidx1 = a.index(eid1)
            if eid2 in a:
                sent_idx2 = self.arr_event_ids.index(a)
                eidx2 = a.index(eid2)
        #print entity_id, sent_idx, eidx
        
        (_, tid1, _, _, _, _) = self.entities[eid1]
        tidx1 = int(tid1)
        (_, tid2, _, _, _, _) = self.entities[eid2]
        tidx2 = int(tid2)

        if sent_idx1 == sent_idx2 and eidx1 != "" and eidx2 != "":
            #if eidx2-3 >= 0:  eid_before = self.arr_event_ids[sent_idx1][eidx2-3]
            #elif eidx2-2 >= 0:  eid_before = self.arr_event_ids[sent_idx1][eidx2-2]
            #else: eid_before = self.arr_event_ids[sent_idx1][eidx2-1]
            eid_before = self.arr_event_ids[sent_idx1][eidx2-1]
            (_, _, tid_before, _, _, _) = self.entities[eid_before]
            tidx_before = int(tid_before)
            (causal_signal, causal_position, csig_tid_arr) = self.__findCausalSignal(str(sent_idx1+1), tidx2-1, tidx_before+1)      #only the ones before e2
            #(causal_signal, causal_position, csig_tid_arr) = self.__findCausalSignal(str(sent_idx1+1), tidx2-1, tidx1+1)            #whole context between e1 and e2
            if causal_signal != "O" and causal_position != "O": causal_position = "BETWEEN"
            
            if causal_signal == "O":
                if eidx1 > 0:
                    #eid_before = self.arr_event_ids[sent_idx1][eidx1-3]
                    eid_before = self.arr_event_ids[sent_idx1][eidx1-1]
                    (_, _, tid_before, _, _, _) = self.entities[eid_before]
                    tidx_before = int(tid_before)
                    
                    (causal_signal, causal_position, csig_tid_arr) = self.__findCausalSignal(str(sent_idx1+1), tidx1-1, tidx_before+1)
                    if causal_signal != "O" and causal_position != "O": causal_position = "BEFORE"
                else:
                    tid_begin = self.sentences_start[sent_idx1]
                    tidx_begin = int(tid_begin)
                    (causal_signal, causal_position, csig_tid_arr) = self.__findCausalSignal(str(sent_idx1+1), tidx1-1, tidx_begin)
                    if causal_signal != "O" and causal_position != "O": causal_position = "BEGIN"   
                    
            #if causal_signal == "O":
            #    if eidx2 < len(self.arr_event_ids[sent_idx1])-1:
            #        eid_after = self.arr_event_ids[sent_idx1][eidx2+1]
            #        (_, _, tid_after, _, _, _) = self.entities[eid_after]
            #        tidx_after = int(tid_after)
            #        
            #        (causal_signal, causal_position, csig_tid_arr) = self.__findCausalSignal(str(sent_idx1+1), tidx_after-1, tidx2+1)
            #        if causal_signal == "as-a-result" and causal_position != "O": causal_position = "AFTER"
            #    else:
            #        tid_last = self.sentences_end[sent_idx1]
            #        tidx_last = int(tid_last)
            #        (causal_signal, causal_position, csig_tid_arr) = self.__findCausalSignal(str(sent_idx1+1), tidx_last, tidx2+1)
            #        if causal_signal == "as-a-result" and causal_position != "O": causal_position = "AFTER"   
                    
        elif sent_idx1 != sent_idx2 and eidx1 != "" and eidx2 != "":
            #print eidx1, self.tokens[tid1][2], str(sent_idx1+1), eidx2, self.tokens[tid2][2], str(sent_idx2+1)
            tid_begin = self.sentences_start[sent_idx2]
            tidx_begin = int(tid_begin)
            eid_after = self.arr_event_ids[sent_idx2][0]
            (_, _, tid_after, _, _, _) = self.entities[eid_after]
            tidx_after = int(tid_after)            
            (causal_signal, causal_position, csig_tid_arr) = self.__findCausalSignal(str(sent_idx2+1), tidx_after-1, tidx_begin)
            if causal_signal != "O" and causal_position != "O": causal_position = "BEGIN-BETWEEN"
            else:
                tid_begin = self.sentences_start[sent_idx1]
                tidx_begin = int(tid_begin)
                eid_after = self.arr_event_ids[sent_idx1][0]
                (_, _, tid_after, _, _, _) = self.entities[eid_after]
                tidx_after = int(tid_after)   
                (causal_signal, causal_position, csig_tid_arr) = self.__findCausalSignal(str(sent_idx1+1), tidx_after-1, tidx_begin)
                if causal_signal != "O" and causal_position != "O": causal_position = "BEGIN-BEFORE"

        (dep_e1, dep_e2) = ("O", "O")
        
        if causal_signal != "O" and csig_tid_arr != []:
            (_, tid1, _, _, _, _) = self.entities[eid1]
            (_, tid2, _, _, _, _) = self.entities[eid2] 
            
            for tid in csig_tid_arr:
                (dep_e1, _) = self.getDependencyPath(tid, tid1)
                if dep_e1 != "O": break    
            for tid in csig_tid_arr:
                (dep_e2, _) = self.getDependencyPath(tid, tid2)
                if dep_e1 != "O": break
        
        return (causal_signal, causal_position, dep_e1, dep_e2)
        
    def __containDigits(self, expression):
        _digits = re.compile('\d')
        return bool(_digits.search(expression))
        
    def getRelTypeRule(self, temp_signal, pair_order, eventclass, tmx_type, tmx_value, eid):
        reltype_rule = "O"
        if self.lang == "it":
            if temp_signal == "entro":
                if tmx_type == "TIME":
                    if pair_order == "et": reltype_rule = "BEFORE"
                    else: reltype_rule = self.getInverseRelation("BEFORE")
                elif tmx_type == "DATE": 
                    if pair_order == "et": reltype_rule = "ENDED_BY"
                    else: reltype_rule = self.getInverseRelation("ENDED_BY")
                elif tmx_type == "DURATION":
                    reltype_rule = "NO-REL"
                    #TODO: empty timex
            elif temp_signal == "tra":
                if tmx_type == "DURATION":
                    if pair_order == "et": reltype_rule = "AFTER"
                    else: reltype_rule = self.getInverseRelation("AFTER")
            elif (temp_signal == "fino a/det" or temp_signal == "fino a" or temp_signal == "fino ad") and tmx_type == "DURATION":
                reltype_rule = "NO-REL"
                #TODO: empty timex
            elif temp_signal == "da" or temp_signal == "da/det":
                if tmx_type == "DATE":
                    if pair_order == "et": reltype_rule = "BEGUN_BY"
                    else: reltype_rule = self.getInverseRelation("BEGUN_BY")
                elif tmx_type == "DURATION":
                    reltype_rule = "MEASURE"
            elif temp_signal == "in" or temp_signal == "in/det":
                if tmx_type == "DURATION" and self.__containDigits(tmx_value):
                    if pair_order == "et": reltype_rule = "AFTER"
                    else: reltype_rule = self.getInverseRelation("AFTER")
                elif tmx_type == "DURATION" and not self.__containDigits(tmx_value):
                    if pair_order == "et": reltype_rule = "IS_INCLUDED"
                    else: reltype_rule = self.getInverseRelation("IS_INCLUDED")
            elif temp_signal == "per":
                if tmx_type == "DURATION":
                    reltype_rule = "MEASURE"
                    
        elif self.lang == "en":
            tmx_rule = self.getTimexRule(eid)
            if tmx_rule != "O" and (tmx_type == "DATE" or tmx_type == "TIME"):
                if tmx_rule == "TMX-BEGIN":
                    reltype_rule = "BEGUN_BY"
                elif tmx_rule == "TMX-END":
                    reltype_rule = "ENDED_BY"
            
        return reltype_rule

    def __isMainEvent(self, ev_id):
        tid = self.entities[ev_id][1]
        sid = self.tokens[tid][1]
        tid_end = self.sentences_end[int(sid)-1]
        if (tid, tid_end) in self.dependencies and self.dependencies[(tid, tid_end)] == "P":
            return True
        else:
            return False

    def getDependency(self, tid1, tid2):
        if tid1 in self.dependencies:
            if tid2 in self.dependencies[tid1]:
                return (self.dependencies[tid1][tid2], "normal")
        elif tid2 in self.dependencies:
            if tid1 in self.dependencies[tid2]:
                return (self.dependencies[tid2][tid1], "reverse")
        
        return ("O", "O")  

    def __generateDependencyPath(self, gov, dep, paths, pathSoFar="", visited=[]):
        if gov in self.dependencies and gov not in visited:
            visited.append(gov)
            for key in self.dependencies[gov].keys():
                if key == dep:
                    paths.append(pathSoFar+"-"+self.dependencies[gov][key])
                else:
                    self.__generateDependencyPath(key, dep, paths, pathSoFar+"-"+self.dependencies[gov][key], visited)
                    
    def getDependencyPath(self, tid1, tid2):
        normal_paths = []
        self.__generateDependencyPath(tid1, tid2, normal_paths, "", [])
        if len(normal_paths) > 0: 
            return (normal_paths[0][1:], "normal")
        reverse_paths = []
        self.__generateDependencyPath(tid2, tid1, reverse_paths, "", [])
        if len(reverse_paths) > 0: 
            return (reverse_paths[0][1:], "reverse")
        return ("O", "O")
        
    def __generatePOSPath(self, gov, paths=[]):
        if self.parser == "stanford" or self.parser == "cc":
            if gov in self.dependencies:
                for key in self.dependencies[gov]:
                    if key in self.tokens:
                        (token, sentid, lemma, pos, mainvb, entity, chunk, conn, mainpos, tense, aspect, pol, supersense) = self.tokens[key]
                        if self.dependencies[gov][key] == "aux":
                            paths.append(key)
                            self.__generatePOSPath(key, paths)
                        elif self.dependencies[gov][key] == "ncmod" and pos == "RB":
                            paths.append(key)
                            #self.__generatePOSPath(key, paths)
        else:   #nr
            for key in self.dependencies:
                if key in self.tokens:
                    (token, sentid, lemma, pos, mainvb, entity, chunk, conn, mainpos, tense, aspect, pol, supersense) = self.tokens[key]
                    if gov in self.dependencies[key]:
                        if self.dependencies[key][gov] == "VC":
                            paths.append(key)
                            self.__generatePOSPath(key, paths)  
            if gov in self.dependencies:
                for key in self.dependencies[gov]:
                    if key in self.tokens:
                        (token, sentid, lemma, pos, mainvb, entity, chunk, conn, mainpos, tense, aspect, pol, supersense) = self.tokens[key]
                        if self.dependencies[gov][key] == "ADV" and pos[0:2] == "XX":
                            paths.append(key)
                    
    def getPOSPathVerb(self, tid1): #this can be used to signify tense, aspect, and polarity
        (token, sentid, lemma, pos, mainvb, entity, chunk, conn, mainpos, tense, aspect, pol, supersense) = self.tokens[tid1]
        pos_path = ""
        polarity = "POS"
        paths = []
        self.__generatePOSPath(tid1, paths)
        paths = paths[::-1]
        for tok in paths:
            (token2, sentid2, lemma2, pos2, mainvb2, entity2, chunk2, conn2, mainpos2, tense2, aspect2, pol2, supersense2) = self.tokens[tok]
            if self.parser == "stanford" or self.parser == "cc":
                if pos2 == "MD": pos_path += lemma + "."
                elif pos2 == "RB":
                    if lemma2 == "not" or lemma2 == "n't": polarity = "NEG"
                else: pos_path += pos2 + "."
            else:   #nr
                if pos2[0:2] == "XX": polarity = "NEG"
                elif lemma2 == "have": pos_path += "VH."
                else: pos_path += pos2 + "."
        pos_path += pos
        return pos_path, polarity
        
    def getPOSPath(self, tid1): #this can be used to signify tense, aspect, and polarity, including for non-verb events
        (token, sentid, lemma, pos, mainvb, entity, chunk, conn, mainpos, tense, aspect, pol, supersense) = self.tokens[tid1]
        pos_path = pos
        polarity = "POS"
        if pos[0] == "V":
            (pos_path, polarity) = self.getPOSPathVerb(tid1)
        elif pos[0] == "N":
            if self.parser == "stanford" or self.parser == "cc":
                for key1 in self.dependencies:
                    for key2 in self.dependencies[key1]:
                        if key2 == tid1 and (self.dependencies[key1][key2][-4:] == "subj" or self.dependencies[key1][key2][-8:] == "subjpass"):
                            (pos_path, polarity) = self.getPOSPathVerb(key1)
                            break
                        elif key2 == tid1 and self.dependencies[key1][key2][-3:] == "obj":
                            (_, _, _, key1_pos, _, _, _, _, _, _, _, _, _) = self.tokens[key1]
                            if key1_pos == "IN": #"ease(V) up on(IN) price-cutting(N)"
                                for k1 in self.dependencies:
                                    for k2 in self.dependencies[k1]:
                                        if k2 == key1 and (self.dependencies[k1][k2] == "prep" or self.dependencies[k1][k2] == "iobj"): 
                                            (pos_path, polarity) = self.getPOSPathVerb(k1)
                                            break
                            else:
                                (pos_path, polarity) = self.getPOSPathVerb(key1)
                                break
            else:   #nr
                if lemma == "have": pos_path = "VH"
                else:
                    if tid1 in self.dependencies:
                        for key in self.dependencies[tid1]:
                            if key in self.tokens: 
                                (_, _, _, key_pos, _, _, _, _, _, _, _, _, _) = self.tokens[key]
                                if key_pos[0] == "V" and (self.dependencies[tid1][key] == "NMOD" or self.dependencies[tid1][key] == "APPO"):
                                    (pos_path, polarity) = self.getPOSPathVerb(key)
                                    break
                    else:
                        for key in self.dependencies:
                            if tid1 in self.dependencies[key]:
                                if self.dependencies[key][tid1] == "SBJ":
                                    (pos_path, polarity) = self.getPOSPathVerb(key)
                                    break
                                    
        elif pos[0] == "J":
            for key1 in self.dependencies:
                for key2 in self.dependencies[key1]:
                    if key1 == tid1 and self.dependencies[key1][key2] == "cop":
                        (pos_path, polarity) = self.getPOSPathVerb(key2)
                        break
                    elif key2 == tid1 and self.dependencies[key1][key2][-4:] == "comp":
                        (pos_path, polarity) = self.getPOSPathVerb(key1)
                        break
        
        if self.parser == "stanford" or self.parser == "cc":             
            if pos[0] == "V" or pos[0] == "N":
                pos_path = pos_path.replace("VBN.VB", "VB") #passive voice, "is destroyed(VBN)"
                pos_path = pos_path.replace("VB.VB", "VB") #"do not know(VB)"
                pos_path = pos_path.replace("VBP", "VBZ") #VBP and VBZ are both for present verbs, VBP (non-3rd person), VBZ (3rd person)
        else:   #nr
            pos_path = pos_path.replace("VVB.VVN", "VVB") #passive voice
            pos_path = pos_path.replace("VVN.VVN", "VVN") #passive voice
            pos_path = ''.join([i for i in pos_path if not i.isdigit()])
                        
        return (pos_path, polarity)

    def getDistance(self, sentid1, sentid2, eidx1, eidx2):
        if sentid1 == "O" or sentid2 == "O":
            sent_distance = -1
        else:
            sent_distance = abs(int(sentid1) - int(sentid2))
        if sent_distance == 0:
            ent_distance = abs(eidx1 - (eidx2-1))
        else:
            ent_distance = -1
        if eidx1 - (eidx2-1) <= 0: ent_order = "normal"
        else: ent_order = "reverse"
        return (sent_distance, ent_distance, ent_order)

    def getLemmaTokenTimex(self, eid):
        (eidx, tid_start, tid_end, _, _, _) = self.entities[eid]
        lemma = "O"
        token = "O"
        if not self.isDCT(eid):
            lemma = ""
            token = ""
            for i in range(int(tid_start), int(tid_end)):
                lemma += self.tokens[str(i)][2] + "_"
                token += self.tokens[str(i)][0] + "_"
            lemma += self.tokens[tid_end][2]
            token += self.tokens[tid_end][0]
        return (lemma, token)
        
    def getInverseRelation(self, rel):
        relations = ["BEFORE", "AFTER", "INCLUDES", "IS_INCLUDED", "DURING", "DURING_INV", "IBEFORE", "IAFTER", "BEGINS", "BEGUN_BY", "ENDS", "ENDED_BY"]
        if rel in relations:
            relIdx = relations.index(rel)
            inverse_rel = ""
            if relIdx % 2 == 0:
                inverse_rel = relations[relIdx+1]
            else:
                inverse_rel = relations[relIdx-1]
            return inverse_rel
        else:
            return None
            
    def getInverseRelation2(self, rel):
        relations = ["BEFORE", "AFTER", "INCLUDES", "IS_INCLUDED", "DURING", "DURING_INV", "IBEFORE", "IAFTER", "BEGINS", "BEGUN_BY", "ENDS", "ENDED_BY"]
        if rel in relations:
            relIdx = relations.index(rel)
            inverse_rel = ""
            if relIdx % 2 == 0:
                inverse_rel = relations[relIdx+1]
            else:
                inverse_rel = relations[relIdx-1]
            return inverse_rel
        else:
            return rel   

    def __getDateComponents(self, date):
        date_cols = date.split("-")
        (y, m, d, mr, era) = (0,0,0,[],"")
        if len(date_cols) == 1:
            if date_cols[0].isdigit(): y = int(date_cols[0])
            else: era = date_cols[0]
        elif len(date_cols) == 2:
            if date_cols[1].isdigit(): (y, m) = (int(date_cols[0]), int(date_cols[1]))
            elif date_cols[1][0] == "Q":
                if date_cols[1][1].isdigit(): m = int(date_cols[1][1])
                if date_cols[1][1] == "1":
                    mr.append(1)
                    mr.append(2)
                    mr.append(3)
                elif date_cols[1][1] == "2":
                    mr.append(4)
                    mr.append(4)
                    mr.append(6)
                elif date_cols[1][1] == "3":
                    mr.append(7)
                    mr.append(8)
                    mr.append(9)
                elif date_cols[1][1] == "4":
                    mr.append(10)
                    mr.append(11)
                    mr.append(12)
        elif len(date_cols) == 3 and date_cols[1].isdigit() and date_cols[2].isdigit():
            (y, m, d) = (int(date_cols[0]), int(date_cols[1]), int(date_cols[2]))
        return (y, m, d, mr, era)
        
    def __getDateRelation(self, y1, m1, d1, mr1, y2, m2, d2, mr2):
        if y1 < y2: return "BEFORE"
        elif y1 > y2: return "AFTER"
        else:
            if mr1 != [] and mr2 == [] and m2 in mr1: return "INCLUDES"
            elif mr1 == [] and mr2 != [] and m1 in mr2: return "IS_INCLUDED"
            elif mr1 != [] and mr2 != []:
                if m1 < m2: return "BEFORE"
                elif m1 > m2: return "AFTER"
                else: return "SIMULTANEOUS"
            else:
                if m1 < m2: return "BEFORE"
                elif m1 > m2: return "AFTER"
                else:
                    if d1 < d2: return "BEFORE"
                    elif d1 > d2: return "AFTER"
                    else: return "SIMULTANEOUS"
            
    def __getTmxDateRelation(self, date1, date2, dct):
        era = ["PAST_REF", "PRESENT_REF", "FUTURE_REF"]
        (y1, m1, d1, mr1, era1) = self.__getDateComponents(date1)
        (y2, m2, d2, mr2, era2) = self.__getDateComponents(date2)
        (y3, m3, d3, mr3, era3) = self.__getDateComponents(dct.split("T")[0])
        
        if era1 != "" and era2 != "" and era1 in era and era2 in era:
            if era.index(era1) < era.index(era2): return "BEFORE"
            elif era.index(era1) > era.index(era2): return "AFTER"
            else: return "SIMULTANEOUS"
        elif era1 != "" and era1 in era and era2 == "":
            if era1 == "PAST_REF":
                if self.__getDateRelation(y2, m2, d2, mr2, y3, m3, d3, mr3) == "BEFORE": return "INCLUDES"
                else: return "BEFORE"
            elif era1 == "PRESENT_REF":
                if self.__getDateRelation(y2, m2, d2, mr2, y3, m3, d3, mr3) == "SIMULTANEOUS": return "INCLUDES"
                else: return self.__getDateRelation(y2, m2, d2, mr2, y3, m3, d3, mr3)
            elif era1 == "FUTURE_REF":
                if self.__getDateRelation(y2, m2, d2, mr2, y3, m3, d3, mr3) == "AFTER": return "INCLUDES"
                else: return "AFTER"
        elif era1 == "" and era2 != "" and era2 in era:
            if era2 == "PAST_REF":
                if self.__getDateRelation(y1, m1, d1, mr1, y3, m3, d3, mr3) == "BEFORE": return "IS_INCLUDED"
                else: return "AFTER"
            elif era2 == "PRESENT_REF":
                if self.__getDateRelation(y1, m1, d1, mr1, y3, m3, d3, mr3) == "SIMULTANEOUS": return "IS_INCLUDED"
                else: return self.__getDateRelation(y1, m1, d1, mr1, y3, m3, d3, mr3)
            elif era2 == "FUTURE_REF":
                if self.__getDateRelation(y1, m1, d1, mr1, y3, m3, d3, mr3) == "AFTER": return "IS_INCLUDED"
                else: return "BEFORE"
        else: #era1 == "" and era2 == ""
            return self.__getDateRelation(y1, m1, d1, mr1, y2, m2, d2, mr2)
        
        return "NONE"
        
    def __getTimeComponents(self, time):
        time_cols = time.split(":")
        (h, m, s, r) = (0, 0, 0, [])
        if len(time_cols) == 1:
            if time_cols[0].isdigit(): h = int(time_cols[0])
            else:
                if time_cols[0] == "MO": 
                    r.append(1)
                    r.append(2)
                    r.append(3)
                    r.append(4)
                    r.append(5)
                    r.append(6)
                    r.append(7)
                    r.append(8)
                    r.append(9)
                    r.append(10)
                    r.append(11)
                elif time_cols[0] == "AF":
                    r.append(13)
                    r.append(14)
                    r.append(15)
                    r.append(16)
                elif time_cols[0] == "EV":
                    r.append(17)
                    r.append(18)
                    r.append(19)
                    r.append(20)
                elif time_cols[0] == "NI":
                    r.append(21)
                    r.append(22)
                    r.append(23)
                    r.append(24)
                    r.append(0)
        elif len(time_cols) == 2: 
            h = int(time_cols[0])
            m = int(time_cols[1])
        elif len(time_cols) == 3: 
            h = int(time_cols[0])
            m = int(time_cols[1])
            s = int(time_cols[2])
        return (h, m, s, r)
                
    def __getTimeRelation(self, time1, time2):
        partday = ["MO", "AF", "EV", "NI"]
        (h1, m1, s1, r1) = self.__getTimeComponents(time1)
        (h2, m2, s2, r2) = self.__getTimeComponents(time2)
            
        if r1 != [] and r2 == [] and h2 in r1: return "INCLUDES"
        elif r1 == [] and r2 != [] and h1 in r2: return "IS_INCLUDED"
        elif r1 != [] and r2 != []:
            if partday.index(time1) < partday.index(time2): return "BEFORE"
            elif partday.index(time1) > partday.index(time2): return "AFTER"
            else: return "SIMULTANEOUS" 
        else: #r1 == [] and r2 == []
            if h1 < h2: return "BEFORE"
            elif h1 > h2: return "AFTER"
            else:
                if m1 < m2: return "BEFORE"
                elif m1 > m2: return "AFTER"
                else:
                    if s1 < s2: return "BEFORE"
                    elif s1 > s2: return "AFTER"
                    else: return "SIMULTANEOUS"

    def getTimexRel(self):
        for eid1 in self.entity_array:
            for eid2 in self.entity_array:
                if self.isTimex(eid1) and self.isTimex(eid2) and eid1 != eid2:
                    (_, _, _, eid1_type, eid1_value, _) = self.entities[eid1]
                    (_, _, _, eid2_type, eid2_value, _) = self.entities[eid2]
                    (_, _, _, eid_dct_type, eid_dct_value, _) = self.entities[self.entity_array[0]]
                    if eid1_type == "DATE" and eid2_type == "TIME" and eid1_value in eid2_value:
                        self.tmxlink[(eid1, eid2)] = "INCLUDES"
                    elif eid1_type == "TIME" and eid2_type == "DATE" and eid2_value in eid1_value:
                        self.tmxlink[(eid1, eid2)] = "IS_INCLUDED"
                    elif eid1_type == "DATE" and eid2_type == "DATE":
                        if eid1_value == eid2_value: self.tmxlink[(eid1, eid2)] = "SIMULTANEOUS"
                        elif eid1_value in eid2_value: self.tmxlink[(eid1, eid2)] = "INCLUDES"
                        elif eid2_value in eid1_value: self.tmxlink[(eid1, eid2)] = "IS_INCLUDED"
                        else: #eid1_value != eid2_value
                            self.tmxlink[(eid1, eid2)] = self.__getTmxDateRelation(eid1_value, eid2_value, eid_dct_value)
                    elif eid1_type == "TIME" and eid2_type == "TIME":
                        if len(eid1_value.split("T")) == 1: (eid1_date, eid1_time) = (eid1_value, "0")
                        else: (eid1_date, eid1_time) = eid1_value.split("T")
                        if len(eid2_value.split("T")) == 1: (eid2_date, eid2_time) = (eid2_value, "0")
                        else: (eid2_date, eid2_time) = eid2_value.split("T")
                        if eid1_date == eid2_date:
                            self.tmxlink[(eid1, eid2)] = self.__getTimeRelation(eid1_time, eid2_time)
                        else:
                            self.tmxlink[(eid1, eid2)] = self.__getTmxDateRelation(eid1_date, eid2_date, eid_dct_value)

    def __generateCSignalDependency(self, gov, before, csignals=[]):
        if gov in self.dependencies:
            for key in self.dependencies[gov]:
                if before == "":
                    if self.dependencies[gov][key] == "PRP" or self.dependencies[gov][key] == "ADV" or self.dependencies[gov][key] == "PRD" or self.dependencies[gov][key] == "LGS": 
                        if key in self.tokens: csignals.append(key)
                        self.__generateCSignalDependency(key, self.dependencies[gov][key], csignals)
                else:
                    if before == "PRP" and self.dependencies[gov][key] == "DEP":
                        if key in self.tokens: csignals.append(key)
                    elif (before == "ADV" or before == "PRD") and (self.dependencies[gov][key] == "PMOD" or self.dependencies[gov][key] == "AMOD"):
                        if key in self.tokens: csignals.append(key)
                        self.__generateCSignalDependency(key, self.dependencies[gov][key], csignals)
                    elif before == "ADV" and self.dependencies[gov][key] == "ADV":
                        if key in self.tokens: csignals.append(key)
                    elif before == "PMOD" and self.dependencies[gov][key] == "PMOD":
                        if key in self.tokens: csignals.append(key)
                        self.__generateCSignalDependency(key, self.dependencies[gov][key], csignals)
                    elif before == "PMOD" and self.dependencies[gov][key] == "NMOD":
                        if key in self.tokens: csignals.append(key)
        if csignals == []:
            for key in self.dependencies:
                if before == "":
                    if gov in self.dependencies[key] and self.dependencies[key][gov] == "SUB": 
                        if key in self.tokens: csignals.append(key)
                    elif gov in self.dependencies[key] and self.dependencies[key][gov] == "SBJ":
                        self.__generateCSignalDependency(key, "", csignals)
    
    def getCSignalDependency(self, eid):
        (_, tid, _, _, _, _) = self.entities[eid]
        csignals = []
        self.__generateCSignalDependency(tid, "", csignals)
        (csignal_str, csignal_position) = ("O", "O")
        if csignals != []:
            for ttid in csignals: csignal_str += self.tokens[ttid][2] + "-"
            csignal_str = csignal_str[1:-1]
            if csignals[0] < tid: csignal_position = "BEFORE"
            elif csignals[0] > tid: csignal_position = "AFTER"
        return (csignal_str, csignal_position)
        
    def __generateCVerbDependency(self, gov, before):
        if gov in self.tokens:
            mainpos = self.tokens[gov][8]
            if mainpos == "n":
                for key in self.dependencies:
                    if gov in self.dependencies[key]:
                        if before == "":
                            if self.dependencies[key][gov] == "SBJ": 
                                if key in self.tokens: return key
                            elif self.dependencies[key][gov] == "OBJ": 
                                if key in self.tokens: return key
                            elif self.dependencies[key][gov] == "PMOD": 
                                return self.__generateCVerbDependency(key, self.dependencies[key][gov])
                        else:
                            if before == "PMOD" and (self.dependencies[key][gov] == "DIR" or self.dependencies[key][gov] == "ADV"): 
                                if key in self.tokens: return key
            elif mainpos == "v":
                if gov in self.dependencies:
                    for key in self.dependencies[gov]:
                        if before == "":
                            if self.dependencies[gov][key] == "ADV": 
                                if key in self.tokens: return key
                            if self.dependencies[gov][key] == "OBJ" or self.dependencies[gov][key] == "COORD": 
                                return self.__generateCVerbDependency(key, self.dependencies[gov][key])
                        else:
                            if before == "OBJ" and self.dependencies[gov][key] == "SUB": 
                                if key in self.tokens: return key
                            elif before == "COORD" and self.dependencies[gov][key] == "CONJ": 
                                if key in self.tokens: return key
                for key in self.dependencies:
                    if gov in self.dependencies[key]:
                        if before == "":
                            if self.dependencies[key][gov] == "IM": 
                                return self.__generateCVerbDependency(key, self.dependencies[key][gov])
                        else:
                            if before == "IM" and self.dependencies[key][gov] == "OPRD": 
                                if key in self.tokens: return key
        return ""
    
    def getCVerbDependency(self, eid):
        (_, tid, _, _, _, _) = self.entities[eid]
        (cverb_str, cverb_position) = ("O", "O")
        if self.__generateCVerbDependency(tid, "") != "":
            cverb = self.__generateCVerbDependency(tid, "")
            cverb_str = self.tokens[cverb][2]
            if cverb < tid: cverb_position = "BEFORE"
            elif cverb > tid: cverb_position = "AFTER"
        return (cverb_str, cverb_position)
    
    def getFeatures(self):
        i = 0
        for line in self.content.rstrip().split('\n'):
            if line != "" and "# FILE:" not in line and "# DATE:" not in line and "# FIELDS:" not in line:    #skip the file descriptor
                self.parseLine(line)
            i += 1
        self.sentences_end.append(self.tokenid)
        
#main
if __name__ == '__main__':        
    input_file = open(sys.argv[1], "r")
    ff = FileFeatures(input_file.read(), "", "en", "nr")
    ff.getFeatures()        
    
    ###testing purpose###
    #print ff.dependencies
    #print ff.tokens
    #print ff.sentences_start
    #print ff.sentences_end
    #print ff.entities
    #print ff.entity_array
    #print ff.tlink
    #print ff.tmxlink
    #for (e1, e2) in ff.tlink:
    #    if ff.tlink[(e1, e2)] != "NONE": print e1, e2, ff.tlink[(e1, e2)]
    #    print e1, e2, ff.getTemporalConnective(e1)
    #    print e1, e2, ff.getTemporalConnective(e2)
    #    print e1, e2, ff.getTemporalSignal(e1)
    #    print e1, e2, ff.getTemporalSignal(e2)
    #for (e1, e2) in ff.clink:
    #    print e1, ff.getCSignalDependency(e1)
    #    print e2, ff.getCSignalDependency(e2)
    #    print e1, ff.getCVerbDependency(e1)
    #    print e2, ff.getCVerbDependency(e2)
    #    print e1, e2, ff.clink[(e1, e2)]
    #for key in ff.csignals:
    #    if "cs" in key:
    #        (_, tid_start, tid_end, _, _, _) = ff.csignals[key]
    #        tidx_start = ff.arr_tokens.index(tid_start)
    #        tidx_end = ff.arr_tokens.index(tid_end)
    #        csignal = ""
    #        for i in range(tidx_start, tidx_end+1):
    #            csignal += ff.tokens[ff.arr_tokens[i]][2] + " "
    #        print csignal[:-1]
    
    #print ff.getDependencyPath('48', '57')
    #print ff.coref_events
            
    #print ff.__isMainEvent("pr1")
    
    #for e in ff.entities:
    #    if e[0] == "e": 
    #        ff.getCSignalDependency(e)
    #        tid = ff.entities[e][2]
    #        (token, sentid, lemma, pos, mainvb, entity, chunk, conn, mainpos, tense, aspect, pol) = ff.tokens[tid]
    #        (pos_path, polarity) = ff.getPOSPath(tid)
    #        if pos[0] == "J":
    #        print tid, pos_path, polarity, tense, aspect, pol
