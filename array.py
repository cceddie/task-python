#!/usr/bin/python


tswe = []   # Title, start, width, end

start = 0
title = ['ID', 'UUID', 'Project', 'Pri', 'Pri', 'Added', 'Started', 'Completed', 'Due', 'Countdown', 'Countdown', 'Age', 'Age', 'Active', 'Tags', 'Deps', 'Recur', 'R', 'T', 'Wait', 'Description'] 
width = [3, 36, 9, 3, 6, 10, 10, 9, 10, 9, 9, 7, 4, 6, 46, 4, 9, 1, 1, 4, 867]
count = 0
asdfg = [] 

print zip(title, width)
print " "


for colTitle in title:
    print title[count], 
    end = start + width[count]
    
    print "start: ", start,
    print "width: ", width[count],
    print "  end: ", end, 
    
    tswe.append( (title[count], start, width[count], end) )

    start = start + width[count] + 1 
    # there is a space between columns
    count = count + 1
    
    print
    
print tswe
