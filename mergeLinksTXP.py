import sys
import os

def ensureDir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
        
def getFieldValueTxp(fieldname, cols):
    fields = ["token", "token_id", "sent_id", "nr_pos", "nr_lemma", "nr_deps", "tmx_id", "tmx_type", "tmx_value", "nr_ner", "ev_class", "ev_id", "role1", "role2", "role3", "is_arg_pred", "has_semrole", "nr_chunk", "nr_main_verb", "nr_connective", "nr_morpho", "ev_tense+ev_aspect+ev_pol", "nr_coevent", "tlink"]
    
    if fieldname in fields:
        if fields.index(fieldname) < len(cols): return cols[fields.index(fieldname)]
        else: return "O"
    else: return "O"

def printUsage():
    print "usage: python mergeLinksTXP.py dir_txp dir_tlink dir_clink dir_output [-fixtlink]"
    print "or     python mergeLinksTXP.py file_txp file_tlink file_clink dir_output [-fixtlink]"

def mergeLinks(filetxp, filetlink, fileclink, outfile, fixtlink):
    ftxp = open(filetxp, 'r')
    ftlink = open(filetlink, 'r')
    fclink = open(fileclink, 'r')
    fout = open(outfile, 'w')
    
    txp_lines = ftxp.readlines()
    tlink_lines = ftlink.readlines()
    clink_lines = fclink.readlines()

    tlink_pairs = {}
    for line in tlink_lines:
        if line != "":
            cols = line.strip().split("\t")
            tlink_pairs[(cols[0], cols[1])] = cols[2]
    
    clinks = {}
    for line in clink_lines:
        if line.strip() != "":
            cols = line.strip().split("\t")
            if cols[2] == "CLINK":
                if cols[0] not in clinks: clinks[cols[0]] = []
                clinks[cols[0]].append(cols[1])
                if fixtlink:
                    tlink_pairs[(cols[0], cols[1])] = "BEFORE"
                    tlink_pairs[(cols[1], cols[0])] = "AFTER"
            elif cols[2] == "CLINK-R":
                if cols[1] not in clinks: clinks[cols[1]] = []
                clinks[cols[1]].append(cols[0])
                if fixtlink:
                    tlink_pairs[(cols[0], cols[1])] = "AFTER"
                    tlink_pairs[(cols[1], cols[0])] = "BEFORE"

    tlinks = {}
    for (source, target) in tlink_pairs:
        reltype = tlink_pairs[(source, target)]
        if source not in tlinks: tlinks[source] = []
        tlinks[source].append((target, reltype))
    
    #file descriptions
    fout.write(txp_lines[0])
    fout.write(txp_lines[1])
    fout.write(txp_lines[2].strip() + "\tclink\n")
    fout.write(txp_lines[3])
    
    #DCT
    fout.write(txp_lines[4])
    fout.write(txp_lines[5])
    
    for line in txp_lines[6:]:
        if line.strip() == "": fout.write(line)
        else:
            cols = line.strip().split("\t")
            line_str = "\t".join(cols[0:-1]) + "\t"
            tmx_id = getFieldValueTxp("tmx_id", cols)
            ev_id = getFieldValueTxp("ev_id", cols)
            #tlink
            if tmx_id != "O" and tmx_id in tlinks:
                for (eid, reltype) in tlinks[tmx_id]:
                    line_str += tmx_id + ":" + eid + ":" + reltype + "||"
                line_str = line_str[0:-2]
            elif ev_id != "O" and ev_id in tlinks:
                for (eid, reltype) in tlinks[ev_id]:
                    line_str += ev_id + ":" + eid + ":" + reltype + "||"
                line_str = line_str[0:-2]
            else:
                line_str += "O"
            line_str += "\t"
            #clink
            if ev_id != "O" and ev_id in clinks:
                for eid in clinks[ev_id]:
                    line_str += ev_id + ":" + eid + "||"
                line_str = line_str[0:-2]
            else:
                line_str += "O"
            fout.write(line_str + "\n")
    
    ftxp.close()
    ftlink.close()
    fclink.close()
    fout.close()

#main
if __name__ == '__main__':
    if len(sys.argv) < 5:
        printUsage()
    else:
        dir_out = sys.argv[4]
        if dir_out[-1] != "/": dir_out += "/"
        ensureDir(dir_out)

        fixtlink = False
        if len(sys.argv) > 5 and sys.argv[5] == "-fixtlink":
            fixtlink = True
        
        if os.path.isdir(sys.argv[1]) and os.path.isdir(sys.argv[2]) and os.path.isdir(sys.argv[3]):  #input is directory name
            dirtxp = sys.argv[1]
            dirtlink = sys.argv[2]
            dirclink = sys.argv[3]
            
            if dirtxp[-1] != "/": dirtxp += "/"
            if dirtlink[-1] != "/": dirtlink += "/"
            if dirclink[-1] != "/": dirclink += "/"
            
            #for r, d, f in os.walk(dirtxp):
            for filename in os.listdir(dirtxp):
                if filename.endswith('.txp'):
                    #print filename
                    filetxp = os.path.join(dirtxp, filename)
                    filetlink = os.path.join(dirtlink, filename + ".tlinks")
                    fileclink = os.path.join(dirclink, filename + ".clinks")
                    outfile = dir_out + os.path.basename(filename)
                    mergeLinks(filetxp, filetlink, fileclink, outfile, fixtlink)    
                    
        elif os.path.isfile(sys.argv[1]) and os.path.isfile(sys.argv[2]) and os.path.isfile(sys.argv[3]):   #input is file name
            filetxp = sys.argv[1]
            filetlink = sys.argv[2] 
            fileclink = sys.argv[3]             
            outfile = dir_out + os.path.basename(sys.argv[1])
            mergeTlinks(filetxp, filetlink, fileclink, outfile, fixtlink)

        else:
            printUsage() 
    
