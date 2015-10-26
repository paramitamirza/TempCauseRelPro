import re
import os
import subprocess
import xml.etree.ElementTree as ET

import sys;
reload(sys);
sys.setdefaultencoding("utf8")

class ColumnsToCAT:
    def __init__(self, filename, outfilename):
        self.filename = filename
        self.outfilename = outfilename
        self.entities = {}
        self.eid = 1
        self.rel_id = 0
        
    def __parseTenseAspectPol(self, tense_aspect_pol):
        if tense_aspect_pol != "O" and tense_aspect_pol != "_" :
            tap = tense_aspect_pol.rstrip().split('+')
            return (tap[0], tap[1], tap[2])
        else:
            return ("O", "O", "O")
        
    def __getFieldValueTxp(self, fieldname, cols):
        fields = ["token", "token_id", "sent_id", "nr_pos", "nr_lemma", "nr_deps", "tmx_id", "tmx_type", "tmx_value", "nr_ner", "ev_class", "ev_id", "role1", "role2", "role3", "is_arg_pred", "has_semrole", "nr_chunk", "nr_main_verb", "nr_connective", "nr_morpho", "ev_tense+ev_aspect+ev_pol", "nr_coevent", "tlink", "clink"]

        if fieldname in fields:
            if fields.index(fieldname) < len(cols): return cols[fields.index(fieldname)]
            else: return "O"
        else: return "O"

    def __createEvent(self, node, start_idx, end_idx, eid, eclass, stem, tense, aspect, polarity, modality, pos):
        node.set("m_id", str(self.eid))
        self.entities[eid] = str(self.eid)
        self.eid += 1
        if eclass != "O": node.set("class", eclass)
        if tense != "O": node.set("tense", tense)
        if aspect != "O": node.set("aspect", aspect)
        if polarity != "O": node.set("polarity", polarity)
        #if modality != "O": node.set("modality", modality.replace("_", " "))
        #if pos != "O": node.set("pos", pos)
        #node.set("comment", "")
        #node.set("factuality", "")
        #node.set("certainty", "")
        if stem != "O": node.set("pred", stem)
        #else: node.set("pred", "")

        for i in range(start_idx, end_idx+1):
            anchor = ET.SubElement(node, "token_anchor")
            anchor.set("t_id", str(i))

    def __createTimex(self, node, start_idx, end_idx, tid, ttype, tvalue, tanchor, tfunction, tfunc_in_doc):
        node.set("m_id", str(self.eid))
        self.entities[tid] = str(self.eid)
        self.eid += 1
        if tfunc_in_doc != "O": node.set("functionInDocument", tfunc_in_doc)
        node.set("type", ttype[2:])
        node.set("value", tvalue)
        #if tanchor != "O": node.set("anchorTimeID", tanchor)
        #node.set("beginPoint", "")
        #node.set("endPoint", "")
        #node.set("comment", "")
        #node.set("freq", "")
        #node.set("quant", "") 

        #if tfunc_in_doc == "CREATION_TIME":
        if start_idx != 0 and end_idx != 0:
            for i in range(start_idx, end_idx+1):
                anchor = ET.SubElement(node, "token_anchor")
                anchor.set("t_id", str(i))
        #else:
        #    node.set("RELATED_TO", "")
        #    node.set("TAG_DESCRIPTOR", "Empty_Mark")

    def __createSignal(self, node, start_idx, end_idx, signal_id):
        node.set("m_id", str(self.eid))
        self.entities[eid] = str(self.eid)
        self.eid += 1
        for i in range(start_idx, end_idx+1):
            anchor = ET.SubElement(node, "token_anchor")
            anchor.set("t_id", str(i))

    def __createLinks(self, node, rel_id, rel_type, signal_id, source_id, target_id, signal_name):
        node.set("r_id", str(self.rel_id))
        if rel_type != None: node.set("reltype", rel_type)
        #if signal_id != "O": node.set(signal_name, signal_id)
        #node.set("comment", "")  

        source = ET.SubElement(node, "source")
        source.set("m_id", self.entities[source_id])
        target = ET.SubElement(node, "target")
        target.set("m_id", self.entities[target_id])  

    def __generateLinks(self, rel, link_col, rel_name):
        if link_col != "O" and link_col != "":
            for link in link_col.split("||"):
                x = link.split(":")
                #signal_name = "signalID"
                if rel_name == "CLINK":
                    #(ent_id, relent_id, signal_id) = (x[0], x[1], x[2])
                    (ent_id, relent_id) = (x[0], x[1])
                    #signal_name = "c-signalID"
                    rel_type = None
                else: 
                    #(ent_id, relent_id, rel_type, signal_id) = (x[0], x[1], x[2], x[3])         
                    (ent_id, relent_id, rel_type) = (x[0], x[1], x[2])
                link = ET.SubElement(rel, rel_name)
                self.__createLinks(link, self.rel_id, rel_type, "", ent_id, relent_id, "")
                self.rel_id += 1

    #generate CAT XML tree
    def __generateCATTree(self):
        ftxp = open(self.filename, 'r')
        txp_lines = ftxp.readlines()
        
        doc_name = os.path.splitext(os.path.basename(self.filename))[0]
        doc = ET.Element("Document")
        doc.set("doc_name", doc_name)

        mark = ET.SubElement(doc, "Markables")
        rel = ET.SubElement(doc, "Relations")

        (timex_id, start_tmx, end_tmx) = ("O", 0, 0)
        (event_id, start_ev, end_ev) = ("O", 0, 0)
        (ttype, tvalue, tanchor, tfunction, tfunc_in_doc) = ("", "", "", "", "")
        (eclass, stem, tense, aspect, polarity, modality, pos) = ("", "", "", "", "", "", "")

        (signal_id, start_sig, end_sig) = ("O", 0, 0)
        (csignal_id, start_csig, end_csig) = ("O", 0, 0)

        for line in txp_lines[4:]:
            if line.strip() != "":
                cols = line.strip().split("\t")
                #print len(cols), tid, sid, cols
                
                if cols[0][0:3] == "DCT":
                    (dct_id, dct_type, dct_value) = (self.__getFieldValueTxp("tmx_id", cols), self.__getFieldValueTxp("tmx_type", cols), self.__getFieldValueTxp("tmx_value", cols))
                    timex = ET.SubElement(mark, "TIMEX3")
                    self.__createTimex(timex, 0, 0, dct_id, dct_type, dct_value, "", "", "CREATION_TIME")
                else:
                    #token
                    if self.__getFieldValueTxp("token_id", cols) != "O":
                        (tid, sid) = (self.__getFieldValueTxp("token_id", cols)[1:], self.__getFieldValueTxp("sent_id", cols))
                        num = str(int(tid)-1)
                        tok = ET.SubElement(doc, "token")
                        tok.set("t_id", tid)
                        tok.set("sentence", sid)
                        tok.set("number", num)
                        tok.text = self.__getFieldValueTxp("token", cols)

                    #print (event_id, start_ev, end_ev), (timex_id, start_tmx, end_tmx)

                    #EVENT
                    if self.__getFieldValueTxp("ev_id", cols) != "O":
                        if event_id == "O":
                            (event_id, start_ev, end_ev) = (self.__getFieldValueTxp("ev_id", cols), int(tid), int(tid))
                            (eclass, stem) = (self.__getFieldValueTxp("ev_class", cols), self.__getFieldValueTxp("nr_lemma", cols))
                            (tense, aspect, polarity) = self.__parseTenseAspectPol(self.__getFieldValueTxp("ev_tense+ev_aspect+ev_pol", cols))
                        elif self.__getFieldValueTxp("ev_id", cols) == event_id:
                            end_ev = int(tid)
                        elif self.__getFieldValueTxp("ev_id", cols) != event_id and start_ev != 0 and end_ev != 0:
                            event = ET.SubElement(mark, "EVENT_MENTION")
                            self.__createEvent(event, start_ev, end_ev, event_id, eclass, stem, tense, aspect, polarity, "", "")
                            (event_id, start_ev, end_ev) = (self.__getFieldValueTxp("ev_id", cols), int(tid), int(tid))
                            (eclass, stem) = (self.__getFieldValueTxp("ev_class", cols), self.__getFieldValueTxp("nr_lemma", cols))
                            (tense, aspect, polarity) = self.__parseTenseAspectPol(self.__getFieldValueTxp("ev_tense+ev_aspect+ev_pol", cols))
                    else:
                        if event_id != "O" and start_ev != 0 and end_ev != 0:
                            event = ET.SubElement(mark, "EVENT_MENTION")
                            self.__createEvent(event, start_ev, end_ev, event_id, eclass, stem, tense, aspect, polarity, "", "")
                            (event_id, start_ev, end_ev) = ("O", 0, 0)
                            (eclass, stem, tense, aspect, polarity, modality, pos) = ("", "", "", "", "", "", "")

                    #TIMEX3
                    if self.__getFieldValueTxp("tmx_id", cols) != "O":                    
                        if timex_id == "O":
                            (timex_id, start_tmx, end_tmx) = (self.__getFieldValueTxp("tmx_id", cols), int(tid), int(tid))
                            (ttype, tvalue) = (self.__getFieldValueTxp("tmx_type", cols), self.__getFieldValueTxp("tmx_value", cols))   
                        elif self.__getFieldValueTxp("tmx_id", cols) == timex_id:
                            end_tmx = int(tid)
                        elif self.__getFieldValueTxp("tmx_id", cols) != timex_id and start_tmx != 0 and end_tmx != 0:
                            timex = ET.SubElement(mark, "TIMEX3")
                            self.__createTimex(timex, start_tmx, end_tmx, timex_id, ttype, tvalue, "", "", "")
                            (timex_id, start_tmx, end_tmx) = (self.__getFieldValueTxp("tmx_id", cols), int(tid), int(tid))
                            (ttype, tvalue) = (self.__getFieldValueTxp("tmx_type", cols), self.__getFieldValueTxp("tmx_value", cols))
                            
                    else:
                        if timex_id != "O" and start_tmx != 0 and end_tmx != 0:
                            timex = ET.SubElement(mark, "TIMEX3")
                            self.__createTimex(timex, start_tmx, end_tmx, timex_id, ttype, tvalue, "", "", "")
                            (timex_id, start_tmx, end_tmx) = ("O", 0, 0)
                            (ttype, tvalue, tanchor, tfunction, tfunc_in_doc) = ("", "", "", "", "")

                    #SIGNAL
                    if self.__getFieldValueTxp("signal", cols)!= "O":                    
                        if signal_id == "O":
                            (signal_id, start_sig, end_sig) = (self.__getFieldValueTxp("signal", cols), tid, tid)
                        elif self.__getFieldValueTxp("signal", cols) == signal_id:
                            end_sig = tid
                        elif self.__getFieldValueTxp("signal", cols) != signal_id and start_sig != 0 and end_sig != 0:
                            signal = ET.SubElement(mark, "SIGNAL")
                            self.__createSignal(signal, start_sig, end_sig, signal_id)
                            (signal_id, start_sig, end_sig) = (self.__getFieldValueTxp("signal", cols), tid, tid)
                            
                    else:
                        if signal_id != "O" and start_sig != 0 and end_sig != 0:
                            signal = ET.SubElement(mark, "SIGNAL")
                            self.__createSignal(signal, start_sig, end_sig, signal_id)
                            (signal_id, start_sig, end_sig) = ("O", 0, 0)

                    #C-SIGNAL
                    if self.__getFieldValueTxp("csignal", cols)!= "O":                    
                        if csignal_id == "O":
                            (csignal_id, start_csig, end_csig) = (self.__getFieldValueTxp("csignal", cols), tid, tid)
                        elif self.__getFieldValueTxp("csignal", cols) == csignal_id:
                            end_csig = tid
                        elif self.__getFieldValueTxp("csignal", cols) != csignal_id and start_csig != 0 and end_csig != 0:
                            csignal = ET.SubElement(mark, "C-SIGNAL")
                            self.__createSignal(csignal, start_csig, end_csig, csignal_id)
                            (csignal_id, start_csig, end_csig) = (self.__getFieldValueTxp("csignal", cols), tid, tid)
                            
                    else:
                        if csignal_id != "O" and start_csig != 0 and end_csig != 0:
                            csignal = ET.SubElement(mark, "C-SIGNAL")
                            self.__createSignal(csignal, start_csig, end_csig, csignal_id)
                            (csignal_id, start_csig, end_csig) = ("O", 0, 0)                  
                
                    #tid += 1
                    #num += 1
            #else: 
            #    sid += 1
        
        self.rel_id = len(self.entities) + 1
        for line in txp_lines[4:]:
            if line.strip() != "":
                cols = line.strip().split("\t")
                self.__generateLinks(rel, self.__getFieldValueTxp("tlink", cols), "TLINK") 
                self.__generateLinks(rel, self.__getFieldValueTxp("slink", cols), "SLINK")
                self.__generateLinks(rel, self.__getFieldValueTxp("alink", cols), "ALINK")
                self.__generateLinks(rel, self.__getFieldValueTxp("clink", cols), "CLINK")

        ftxp.close()
        
        return doc
        
    '''
    copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
    it basically walks your tree and adds spaces and newlines so the tree is
    printed in a nice way
    '''
    def __indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.__indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        
    def generateCAT(self):
        #print CAT XML document
        cat_tree = self.__generateCATTree()
        self.__indent(cat_tree)
        outputfile = open(self.outfilename, "w")
        #outputfile.write('<?xml version="1.0" ?>' + ET.tostring(cat_tree, encoding="us-ascii", method="xml"))
        tree = ET.ElementTree(cat_tree)
        tree.write(outputfile)
        outputfile.close()

def ensureDir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
        
def printUsage():
    print "usage: python convertTXPtoCAT.py dir_txp dir_output"
    print "or     python convertTXPtoCAT.py file_txp dir_output"        

#main
if __name__ == '__main__':
    if len(sys.argv) < 3:
        printUsage()
    else:
        dir_out = sys.argv[2]
        if dir_out[-1] != "/": dir_out += "/"
        ensureDir(dir_out)
        
        if os.path.isdir(sys.argv[1]):  #input is directory name
            dirtxp = sys.argv[1]
            if dirtxp[-1] != "/": dirtxp += "/"
            
            #for r, d, f in os.walk(dirtxp):
            for filename in os.listdir(dirtxp):
                if filename.endswith('.txp'):
                    print filename
                    filetxp = os.path.join(dirtxp, filename)
                    if ".naf" in filename: outfile = dir_out + os.path.basename(filename).replace(".naf.txp", ".xml")
                    elif ".tml" in filename: outfile = dir_out + os.path.basename(filename).replace(".tml.txp", ".xml")
                    cat = ColumnsToCAT(filetxp, outfile)
                    cat.generateCAT()
                    
        elif os.path.isfile(sys.argv[1]):   #input is file name
            filetxp = sys.argv[1]        
            if ".naf" in filename: outfile = dir_out + os.path.basename(sys.argv[1]).replace(".naf.txp", ".xml")
            elif ".tml" in filename: outfile = dir_out + os.path.basename(sys.argv[1]).replace(".tml.txp", ".xml")
            cat = ColumnsToCAT(filetxp, outfile)
            cat.generateCAT()

        else:
            printUsage()         

