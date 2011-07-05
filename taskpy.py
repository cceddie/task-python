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

from operator import itemgetter, attrgetter


# -----------------------------------------------------------------------------
# regex compilation

leadSpaces = re.compile('^\ \ \ \ ')
removeSpaces = re.compile('^\ *')
trailBreak = re.compile('\s*$')
leadBreak = re.compile('^[\t\n\r\f\v]*')
trailTask = re.compile('\ task[s]')


# -----------------------------------------------------------------------------
# setting up variables

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
linesToDisplay = win_y - 5


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
			    twse.append( (colNames[count], start, end, colWidthVal[count]) )
			    
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
    tShow  = 'showing xx of ' + taskTotal
        
    right = tBlock + tWait + tShow
    print tStart + right.rjust(win_x - len(tStart) )
    pass
    

# - - - - - 
def sac():
    print "title, start, end"
    for title, width, start, end  in twse:
        print title.rjust(12) + str(start).rjust(5) + str(end).rjust(4)
    	
# - - - - - 
# read the parsing string for output




# =============================================================================
# and here we go...


# need this info first
showWindowDimensions()

# dump stats first as it is a faster, more accurate way to get the stats (duh)
taskPending, taskWaiting, taskRecurring, taskBlocked, taskTotal = getStats()

renderTitleBar(taskPending, taskWaiting, taskRecurring, taskBlocked, taskTotal)

# push task output into a file
dumpTaskToFile()
colNames, colWidthTxt, colWidthVal, twse, taskAll = mergeToOneLine()



print "\n", colNames, colWidthVal

#nothing(colNames, colWidthVal, colWidthTxt)


print twse
print " "
print taskAll[1][0:3], taskAll[1][216:316]
print " "
print taskAll[2][0:3]
print " "
print taskAll[3][216:316]
print " "
print taskAll[4][216:316]
print " "


sac()



