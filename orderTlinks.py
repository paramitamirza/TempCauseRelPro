import sys
import os

def printUsage():
    print "usage: python orderTlinks.py file_tlinks_verbose"

def orderTlinksInFile(infile):
    ftlinks = open(infile, 'r')
    tlink_lines = ftlinks.readlines()
    tlinks = []
    tlinks_prior = []
    for line in tlink_lines:
        cols = line.strip().split("\t")
        if len(cols) > 3:
            label = cols[2]
            labels = cols[3:]
            classes = []
            values = []
            scores = {}
            for l in labels:
                classes.append(l.split("/")[0])
                values.append(float(l.split("/")[1]))
                scores[l.split("/")[0]] = float(l.split("/")[1])
            score = scores[label]
            tlinks.append((cols[0], cols[1], label, score))
        elif len(cols) == 3:
            tlinks_prior.append((cols[0], cols[1], label))

    ordered_tlinks = ""
    for (e1, e2, reltype) in tlinks_prior:
        ordered_tlinks += e1 + "\t" + e2 + "\t" + reltype + "\n"
    sorted_tlinks = sorted(tlinks, key=lambda tup: tup[3], reverse=True)
    for (e1, e2, reltype, score) in sorted_tlinks:
        if score >= 1.5:
            ordered_tlinks += e1 + "\t" + e2 + "\t" + reltype + "\n"

    return ordered_tlinks

#main
if __name__ == '__main__':
    if len(sys.argv) < 2:
        printUsage()
    else:
        if os.path.isfile(sys.argv[1]):   #input is file name
            print orderTlinksInFile(sys.argv[1])
        else:
            printUsage() 
