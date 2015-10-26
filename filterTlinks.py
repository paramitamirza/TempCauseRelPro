import sys
import os
    
def printUsage():
    print "usage: python filterTlinks.py file_tlinks diff_threshold min_threshold"
        
def maxValues(vals):
    first_max = 0
    second_max = 1
    for i in range(2, len(vals)):
        if vals[i] > vals[second_max]: second_max = i
        if vals[second_max] > vals[first_max]:
            temp = first_max
            first_max = second_max
            second_max = temp
    return (first_max, second_max)
    
def filterTlinksInFile(infile, diff_threshold, min_threshold):
    ftlinks = open(infile, 'r')
    tlink_lines = ftlinks.readlines()
    filtered_tlinks = ""
    tlinks = []
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
            #(first_max, second_max) = maxValues(values)
            #if values[first_max] - values[second_max] > diff_threshold and values[first_max] > min_threshold:
            #    filtered_tlinks += cols[0] + "\t" + cols[1] + "\t" + classes[first_max] + "\n"
        #else:
        #    filtered_tlinks +=  line

    sorted_tlinks = sorted(tlinks, key=lambda tup: tup[3], reverse=True)
    for (e1, e2, reltype, score) in sorted_tlinks:
        if score >= 1.5:
            filtered_tlinks += e1 + "\t" + e2 + "\t" + reltype + "\n"

    return filtered_tlinks

#main
if __name__ == '__main__':
    if len(sys.argv) < 4:
        printUsage()
    else:
        if os.path.isfile(sys.argv[1]):   #input is file name
            print filterTlinksInFile(sys.argv[1], float(sys.argv[2]), float(sys.argv[2]))

        else:
            printUsage() 
