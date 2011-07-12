#!/usr/bin/python
# ------------------------------------------------------------------------------
# tcyun
# 
# - changing approach (again) as the new rc.defaultwidth=0 flag allows me to use
#   the default ordering given by task and simplifies a great deal of work.
# 
# - task output re-formatter hack-code
#
#
# TODO
# - remind myself that this code is to learn python, not to impress myself 
#   with my l337 coding skillz
# 
# - finish the regex removing attributes from the array.  
# 
# - consider how output is going to be described...
# 
# - xref sort.py sample that i made.
#   i think we are quite close...
#
# - learn how zip and unzip work w/r/t arrays.  i suspect i'm wasting lots of 
#   lines of code and that those two commands would make life easier...
#
# -----------------------------------------------------------------------------
# OF NOTE
# - at the moment, there is are two description columns.  i use only one
#   of them.  the other appends a plus sign if you have annotations.
#   i care not for that and it is confusing my brain how to deal with it
#   in the program.  so it goes away.
#
# -----------------------------------------------------------------------------
# essentials

import commands
import re
import curses
import os
import time
import subprocess
import sys

#import time

from operator import itemgetter, attrgetter


# -----------------------------------------------------------------------------
# regex compilation

leadSpaces = re.compile('^\ \ \ \ ')
removeSpaces = re.compile('^\ *')
trailBreak = re.compile('\s*$')
leadBreak = re.compile('^[\t\n\r\f\v]*')
trailTask = re.compile('\ task.*$')


# -----------------------------------------------------------------------------
# setting up variables

version = '0.0.0.0.0.0.1 beta'
linenumber=0
colNames=[]
colWidthTxt=[]
colWidthVal=[]

# getting screen size of the terminal... and i assume that this is 
# both portable and correct.  but for my test sample of "my machine" it works
# just fine
#
# note, the python manual says that if initscr has a prob, it may just cause
#       everything to puke.  and that is, as they say, bad

stdscr = curses.initscr()
win_y,win_x=stdscr.getmaxyx()
curses.endwin()
linesToDisplay = win_y - 4 # because your shell might east some extra lines

display = [ 'ID', 'space', 'Project', 'space', 'Due', 'space', 'Priority1', 'Active1', 'space', 'Description' ]
ellipsis = '...'


# -----------------------------------------------------------------------------
def getStats():	
    cmdStats = 'task stats > taskStat'
    cmdBlocked = 'task blocked | tail -1'
    
    os.system(str(cmdStats))
    taskStat = open('taskStat') 
    
    for line in taskStat:
        if re.match("Pending", line):
            dump, pending=line.split()
        elif re.match("Waiting", line):
            dump, waiting = line.split()
        elif re.match ("Recurring", line):
            dump, recurring = line.split()
        elif re.match("Total", line):
            dump, total = line.split()
        else:
            pass
        
    p = subprocess.Popen(cmdBlocked, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    blocked, stderr = p.communicate()
    
    blocked = trailBreak.sub('', blocked)
    blocked = trailTask.sub('', blocked)

    return(pending, waiting, recurring, blocked, total)
    pass


# - - - - - 
def dumpTaskToFile():
	# push task output into a file
	os.system('task tcy-all rc.defaultwidth=0 > taskDump')


# - - - - - 
def mergeToOneLine():	
	# i should write a check to make sure that the dump file exists... meh.
	taskStat = open('taskDump') 	

	# skip first two lines of oddity
	# !!! NOTE !!!
	# the processTaskFile below should be added here...
	#
	#file.next(taskStat)
	#file.next(taskStat)
	#
	prevLine = ""
	lineNum = 0
	taskCount = 0
	
	twse=[]
	taskAll=[] 
	
	for currLine in taskStat:
		
		# remove trailing linefeed, returns, etc
		currLine = trailBreak.sub('', currLine)
		currLine = leadBreak.sub('', currLine)
		
		if lineNum == 0:
			pass
		elif lineNum == 1:
			for columns in currLine.split():
				#print columns
				colNames.append(columns)                                
		elif lineNum == 2:
			for columnwidth in currLine.split():
				#print len(columnwidth)
				colWidthTxt.append(columnwidth)
				colWidthVal.append(len(columnwidth))
			# no put all of this stuff into one nice list
			count = start = end = 0
			
			for colName in colNames:
			    end = start + colWidthVal[count]
			    twse.append( (colNames[count], colWidthVal[count] , start, end) )
			    
			    start = start + colWidthVal[count] + 1
			    count = count + 1
			    
			    
		elif lineNum > 2:
			if leadSpaces.match(currLine):
				currLine = removeSpaces.sub('', currLine)
				prevLine = prevLine + " " + currLine
			else:
				# !!! here, we should dump to another function
				#     that only prints the desired columns
				# which also means that we need to define the
				# desired columns up front...
				#print prevLine 
				displayColumns(taskCount, prevLine)
				taskAll.append(prevLine)
				taskCount = taskCount + 1
				
				prevLine = currLine
		else:
			print "FAIL"	

		lineNum = lineNum + 1
	
	return (colNames, colWidthTxt, colWidthVal, twse, taskAll)


# - - - - - 
def displayColumns (number, line):
    # # print everything.  just dump it.  this is a sample
	# print number, line[0:110]
	# #	
	# #start = 0
	# #buildLine = ""
	# #	
	# #columnDict = zip(colNames,colWidthVal,colWidthTxt)
	# #for item in columnDict:
	# #	names, widthVal, widthTxt = item		
	# #	end = start + int(widthVal)
	# #	buildLine = buildLine + " " + line[start:end]
	# #	
	# #	#print names, start, end 
	# #	#print start, widthVal
	# #	
	# #	start = start + int(widthVal) + 1
	# #
	# #print buildLine
	
	pass


# - - - - - 
def showWindowDimensions():
	print "window dimensions x, y: ", win_x, win_y


# - - - - - 
def renderTitleBar(taskPending, taskWaiting, taskRecurring, taskBlocked, taskTotal):
    tStart = 'task: one page output'
    tBlock = '(' + taskBlocked + ' blocked, ' 
    tWait  = taskWaiting + ' waiting) '
    tShow  = 'showing ' + str(linesToDisplay) + ' of ' + taskTotal
        
    right = tBlock + tWait + tShow
    print tStart + right.rjust(win_x - len(tStart) )
    pass
    
# - - - - - 
def renderTask():
    line = ''
    overallwidth = count = 0 
    
    while count < linesToDisplay:
        count = count + 1
        # put in a catch here to filter lines based on passed params
        # then pass matched line to a render function...
        
        for item in display:
            # there *must* be a smarter way of doing this.  but at 2am, this is
            # is the only thing my brain can handle.  granted, maybe i should
            # not have had that second beer...
            
            if item == 'space':
                line = line + ' '
                overallwidth = overallwidth + 1
            
            elif item == 'ID':
                line = line + taskAll[count][twse[0][2]:twse[0][3]].rjust(twse[0][1])
                overallwidth = overallwidth + len(taskAll[count][twse[0][2]:twse[0][3]])
            
            elif item == 'UUID':
                line = line + taskAll[count][twse[1][2]:twse[1][3]].rjust(twse[1][1]) 
                overallwidth = overallwidth + len(taskAll[count][twse[1][2]:twse[1][3]])
                
            elif item == 'Project':
                line = line + taskAll[count][twse[2][2]:twse[2][3]].rjust(twse[2][1])
                overallwidth = overallwidth + len(taskAll[count][twse[2][2]:twse[2][3]])
                
            elif item == 'Priority1':
                line = line + taskAll[count][twse[3][2]:twse[3][2]+1]
                overallwidth = overallwidth + 1
                
            elif item == 'Pri':
                line = line + taskAll[count][twse[3][2]:twse[3][3]].rjust(twse[3][1])
                overallwidth = overallwidth + len(taskAll[count][twse[3][2]:twse[3][3]])
                
            elif item == 'Priority':
                line = line + taskAll[count][twse[4][2]:twse[4][3]].rjust(twse[4][1])
                overallwidth = overallwidth + len(taskAll[count][twse[4][2]:twse[4][3]])
                
            elif item == 'Added':
                line = line + taskAll[count][twse[5][2]:twse[5][3]].rjust(twse[5][1])
                overallwidth = overallwidth + len(taskAll[count][twse[5][2]:twse[5][3]])
                
            elif item == 'Started':
                line = line + taskAll[count][twse[6][2]:twse[6][3]].rjust(twse[6][1])
                overallwidth = overallwidth + len(taskAll[count][twse[6][2]:twse[6][3]])
                
            elif item == 'Completed':
                line = line + taskAll[count][twse[7][2]:twse[7][3]].rjust(twse[7][1])
                overallwidth = overallwidth + len(taskAll[count][twse[7][2]:twse[7][3]])
                
            elif item == 'Due':
                # insert a loop to change date format if i want
                # insert a loop to catch end of "today" and then print bash underline instead of my goofy script
                line = line + taskAll[count][twse[8][2]:twse[8][3]].rjust(twse[8][1])
                overallwidth = overallwidth + len(taskAll[count][twse[8][2]:twse[8][3]])
                
            elif item == 'Countdown':
                line = line + taskAll[count][twse[9][2]:twse[9][3]].rjust(twse[9][1])
                overallwidth = overallwidth + len(taskAll[count][twse[9][2]:twse[9][3]])
                
            elif item == 'Countdown':
                line = line + taskAll[count][twse[10][2]:twse[10][3]].rjust(twse[10][1])
                overallwidth = overallwidth + len(taskAll[count][twse[10][2]:twse[10][3]])
                
            elif item == 'Age':
                line = line + taskAll[count][twse[11][2]:twse[11][3]].rjust(twse[11][1])
                overallwidth = overallwidth + len(taskAll[count][twse[11][2]:twse[11][3]])
                
            elif item == 'Age':
                line = line + taskAll[count][twse[12][2]:twse[12][3]].rjust(twse[12][1])
                overallwidth = overallwidth + len(taskAll[count][twse[12][2]:twse[12][3]])
                
            elif item == 'Active1':
                line = line + taskAll[count][twse[13][2]:twse[13][2]+1]
                overallwidth = overallwidth + 1
                
            elif item == 'Active':
                line = line + taskAll[count][twse[13][2]:twse[13][3]].rjust(twse[13][1])
                overallwidth = overallwidth + len(taskAll[count][twse[13][2]:twse[13][3]])
                
            elif item == 'Tags':
                line = line + taskAll[count][twse[14][2]:twse[14][3]].rjust(twse[14][1])
                overallwidth = overallwidth + len(taskAll[count][twse[14][2]:twse[14][3]])
                
            elif item == 'Deps':
                line = line + taskAll[count][twse[15][2]:twse[15][3]].rjust(twse[15][1])
                overallwidth = overallwidth + len(taskAll[count][twse[15][2]:twse[15][3]])
                
            elif item == 'Recur':
                line = line + taskAll[count][twse[16][2]:twse[16][3]].rjust(twse[16][1])
                overallwidth = overallwidth + len(taskAll[count][twse[16][2]:twse[16][3]])
            
            elif item == 'R':
                line = line + taskAll[count][twse[17][2]:twse[17][3]].rjust(twse[17][1])
                overallwidth = overallwidth + len(taskAll[count][twse[17][2]:twse[17][3]])
            
            elif item == 'T':
                line = line + taskAll[count][twse[18][2]:twse[18][3]].rjust(twse[18][1])
                overallwidth = overallwidth + len(taskAll[count][twse[18][2]:twse[18][3]])
                
            elif item == 'Wait':
                line = line +  taskAll[count][twse[19][2]:twse[19][3]].rjust(twse[19][1])
                overallwidth = overallwidth + len(taskAll[count][twse[19][2]:twse[19][3]])
            
            elif item == 'Description':
                # get the overall width calculation done here for the rjust
                # ...in fact, might have to pre-calculate it as there might be something
                # to the right of descrip...
                
                # if len(descrip) > remainin space, crop and add ellipses
                # else, just pass through
                
                
                if ( len(taskAll[count][twse[20][2]:]) + len(line) ) > win_x:
                    line = line + taskAll[count][twse[20][2]:twse[20][2]+(win_x - overallwidth - len(ellipsis) )]
                    line = line + ellipsis
                    overallwidth = overallwidth + len(taskAll[count][twse[20][2]:twse[20][2]+(win_x - overallwidth - len(ellipsis) )] )
                    
                else:
                    line = line + taskAll[count][twse[20][2]:twse[20][2]+(win_x - overallwidth )]
                    overallwidth = overallwidth + len(taskAll[count][twse[20][2]:twse[20][2]+(win_x - overallwidth )] )
                        
            else:
                print "something bad happened"
                pass
    
        print line
        line = ''
        overallwidth = 0


# - - - - - 
def dumpTWSE():
    print "printing the full TWSE table"
    
    print "title, width, start, end"
    count = 0 
    for title, width, start, end  in twse:
        
        print str(count).rjust(3) + title.rjust(12) + str(width).rjust(5) + str(start).rjust(5) + str(end).rjust(5) 
        count = count + 1
        
    print "\n\n"
    	
# - - - - - 
# read the parsing string for output




# =============================================================================
# and here we go...


# dump stats first as it is a faster, more accurate way to get the stats (duh)
taskPending, taskWaiting, taskRecurring, taskBlocked, taskTotal = getStats()

renderTitleBar(taskPending, taskWaiting, taskRecurring, taskBlocked, taskTotal)

# push task output into a file
dumpTaskToFile()
colNames, colWidthTxt, colWidthVal, twse, taskAll = mergeToOneLine()


# some helper info to determine what all the various variables are
# should generally not need to use these

# showWindowDimensions()
# dumpTWSE()

#renderColumnTitles()

renderTask()
#
#
#try:
#    sys.argv[1]
#except:
#    print 'nothing passed'
#else:
#    if sys.argv[1] == 'help' or sys.argv[1] == '?' :
#        print 'print from the help file'
#    elif sys.argv[1] == 'Help':
#        print 'print task help (not my script)'
#    elif sys.argv[1] == 'License':
#        print 'dump GPL nonsense'
#    elif sys.argv[1] == 'Aldus':
#        print 'Aldus'
#    elif sys.argv[1] == 'Torsten':
#        print 'Torsten'
#    elif sys.argv[1] == 'children' or sys.argv[1] == 'kids' or sys.argv[1] == 'parenting' or sys.argv[1] == 'parent' :
#        print 'parenting, both kids'
#    elif sys.argv[1] == 'computer' or sys.argv[1] == 'mac'  or sys.argv[1] == 'Mac' :
#        print 'print computer'
#    elif sys.argv[1] == 'home': 
#        print 'print home  '
#    elif sys.argv[1] == 'movie' or sys.argv[1] == 'music' or sys.argv[1] == 'tv': 
#        print 'movie/music/tv  '
#    elif sys.argv[1] == 'read' or sys.argv[1] == 'book' :
#        print 'books and reading  '
#    elif sys.argv[1] == 'work':
#        print 'work, nexpres, expres, jive   '
#    elif sys.argv[1] == 'version':
#        print 'version ', version
#    else:
#        print 'nothing passed'
#











