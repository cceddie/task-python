#!/opt/local/bin/python

display=['space', 'ID', 'space', 'ID' ]
overallwidth = 0

count = 0 
while count < 10:
    line = ''
    for item in display:
        if item == "space":
            line = line + " "
            overallwidth = overallwidth + 1
        elif item == "ID":
            line = line + item
            overallwidth = overallwidth + 10
    count = count + 1
    print count, overallwidth, line
    

print line
print overallwidth
