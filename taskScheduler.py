#! /usr/bin/python

import yaml
import operator, datetime, sys, os

#                                                                                                                       #
# This program takes an input of task in a YAML file format, schedules tasks without times and prints the full schedule.#
#                                                                                                                       #           

# Fuction to open file
# @param pathToFile YAML-File
# @return doc Dict of tasks
def openFile(pathToFile):
    with open(pathToFile) as stream:
        try:
            doc = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return doc

# Sorts tasks by duration, ascending
def sortByDuration(taskList):
    return sorted(taskList, key=operator.itemgetter('duration'))

# Sorts list by duratio,n descending
def sortByDurationRev(taskList):
    return sorted(taskList, key=operator.itemgetter('duration'),reverse=True)

# Sorts list by start
def sortByStart(taskList):
    return sorted(taskList, key=operator.itemgetter('start'))

# Sorts list by end
def sortByEnd(taskList):
    return sorted(taskList, key=operator.itemgetter('end'))

# Seperates tasks with assigned times and adds time condition
# @param taskList 
# @return taskList of tasks with times
def tasksWithTimes(taskList):
    nonNullList=[]
    for task in taskList:
        if task['start'] != None:
            nonNullList.append(task)
            task['timeCondition'] = True        
    nonNullList = sortByStart(nonNullList)
    return nonNullList

# Seperates tasks without assigned times and adds time condition
# @param taskList 
# @return taskList of tasks without assigned times
def tasksToBeTimed(taskList):
    nullList=[]
    for task in taskList:
        if task['start'] == None:
            nullList.append(task)
            task['timeCondition'] = False
    nullList = sortByDuration(nullList)        
    return nullList

# Assigns startTime, end, endTime, and durTime to dictionary entries
# @param taskList
# @return taskList
def assignTimesToDict(taskList):
    for task in taskList:
        startTime = task["start"]
        dur = task["duration"]
        startAsTime = datetime.datetime.strptime(startTime, '%H:%M')
        endAsTime = startAsTime + datetime.timedelta(minutes=dur) 
        endTime = datetime.datetime.strftime(endAsTime,'%H:%M')
        task["end"] = endTime
        task["startTime"] = startAsTime
        task["endTime"] = endAsTime
        task["durTime"] = calcDurTime(task)
    return taskList

# Checks if two tasks are compatable
# @param task1  
# @param task2
# @return boolean
def compatable(task1, task2):
    task1Id = task1["id"]
    task2CompList = task2["compatibility"]
    if task2CompList == None or task1Id == None:
        return False
    if task1Id in task2CompList:
        return True
    else:
        return False

# Calculates the lowest end time of two tasks
# @param task1  
# @param task2
# @return end
def calcLeastEndTime(task1, task2):
    if task1["endTime"] < task2["endTime"]:
        return task1["end"]
    elif task2["endTime"] < task1["endTime"]:
        return task2["end"]

# Calculates the greatest end time of two tasks
# @param task1  
# @param task2
# @return end
def calcGreaterEndTime(task1, task2):
    if task1["endTime"] > task2["endTime"]:
        return task1["end"]
    elif task2["endTime"] > task1["endTime"]:
        return task2["end"]

# Determines which of two tasks has least end time
# @param task1  
# @param task2
# @return task with least endTime
def taskWithLeastEndTime(task1,task2):
    if task1["endTime"] < task2["endTime"]:
        return task1
    else:
        return task2

# Determines which of two tasks has greatest end time
# @param task1  
# @param task2
# @return task with greatest endTime
def taskWithGreaterEndTime(task1,task2):
    if task1["endTime"] > task2["endTime"]:
        return task1
    else:
        return task2

# Calculates differece in start time of two tasks
# @param task1  
# @param task2
# @return difference in start times as datetime
def calcDifInStarts(task1, task2):
    return task2["startTime"] - task1["startTime"]

# Calculates duration as datetime
# @param task
# @return duration as datetime
def calcDurTime(task):
    dur = task["duration"]
    return datetime.timedelta(minutes=dur)

# Calculates start as datetime
# @param task
# @retrun start as datetime
def calcStartTime(task):
    startTime = task["start"]
    return datetime.datetime.strptime(startTime, '%H:%M')

# Checks if a time is between two times
# @param startTime Begining of timespan to check between
# @param endTime End of timespan to check between
# @return boolean
def timeIsBetween(startTime,endTime,timeToCheck):
    if startTime < endTime:
        return timeToCheck > startTime and timeToCheck < endTime

# Creates schedule using the time constraints of times with assigned tasks
# @param taskList
# @return A Partially complete schedule
def createSchedule(taskList):
    timed = tasksWithTimes(taskList)
    assignTimesToDict(timed)
    unTimed = tasksToBeTimed(taskList)
    tasks = timed + unTimed
    A = []
    k = 0
    j=0
    if len(A) == 0:
        A.append(tasks[0])
    for m in range(1,len(tasks)):
        if tasks[m] in timed:
            if tasks[k]['end'] > tasks[m]['start'] and compatable(tasks[k],tasks[m]):
                A.append(tasks[m])
                k=m               
            elif tasks[k]['end'] <= tasks[m]['start']:
                A.append(tasks[m])
                k=m
            else:
                print("Unable to schedule tasks due to compatability conflict")
        
        if tasks[m] in unTimed:
            for a in range(1, len(A)):
                if calcDifInStarts(A[j], A[a]) > calcDurTime(tasks[m]) and compatable(A[j],tasks[m]):
                    leastEnd = calcLeastEndTime(A[j],A[j+1])
                    greaterEnd = calcGreaterEndTime(A[j],A[j+1])
                    taskWithGreaterEnd = taskWithGreaterEndTime(A[j],A[j+1])
                    taskWithLeastEnd = taskWithLeastEndTime(A[j],A[j+1])                    
                    if compatable(taskWithLeastEnd,tasks[m]):
                        tasks[m]['start'] = leastEnd
                    elif compatable(taskWithGreaterEnd, tasks[m]):
                        tasks[m]['start'] = greaterEnd                    
                    A.append(tasks[m])
                    A = assignTimesToDict(A)
                    A = sortByStart(A)
                    j=a               
    return A

# Adds the remaining unscheduled tasks to lists
# @param taskList1 Original list of tasks
# @param taskList2 Partially complete schedule from createSchedule
# @return taskList2 Non-Optimized schedule      
def addTheRest(taskList1, taskList2):
    taskList1 = sortByDurationRev(taskList1)
    for task in taskList1:
        if task not in taskList2:
                if compatable(task,taskList2[len(taskList2)-1]) and not(timeIsBetween(taskList2[len(taskList2)-2]['startTime'],taskList2[len(taskList2)-2]['endTime'], taskList2[len(taskList2)-1]['startTime'])) and not(timeIsBetween(taskList2[len(taskList2)-2]['startTime'],taskList2[len(taskList2)-2]['endTime'], taskList2[len(taskList2)-1]['endTime'])):
                    task['start'] = taskList2[len(taskList2)-1]['start']
                    taskList2.append(task)
                    assignTimesToDict(taskList2)
                else:
                    task['start'] = taskList2[len(taskList2)-1]['end']
                    taskList2.append(task)
                    assignTimesToDict(taskList2)
    return taskList2

# Removes any compatability collisions
# @param total List of tasks
# @return A List of tasks without compatability collisions
def fixNonCompatIssue(total):
    A=[]
    for task1 in range(0,len(total)):
        for task2 in range(1,len(total)):
            if not(compatable(total[task1], total[task2])) and (timeIsBetween(total[task1]['startTime'],total[task1]['endTime'],total[task2]['startTime']) or timeIsBetween(total[task1]['startTime'],total[task1]['endTime'],total[task2]['endTime'])) and not(total[task1]['description'] == total[task2]['description']):
                if total[task1]['timeCondition'] == False:
                    total[task1]['start'] = total[task2]['end']
                    A = assignTimesToDict(total)
                    A = sortByStart(total)
                elif total[task1]['timeCondition'] == True:
                    total[task2]['start'] = total[task1]['end']
                    A = assignTimesToDict(total)
                    A = sortByStart(total)                       
    return A

# Prints final schedule
# @param taskList Final schedule of tasks
def printSchedule(taskList):
    taskList = sortByEnd(taskList)
    taskList = sortByStart(taskList)
    for task in taskList:
        print(task['description'] + ','+ task["start"] + ' ' + task['end'])



######## Main Function ########

argLen = len(sys.argv)
usage = '\nNAME\n \ttaskScheduler [path_to_file]\n\nSYNOPSIS\n\tTakes an input of task in a YAML file, schedules the tasks and prints the full schedule\n\n'

# Checks if argument is of correct length and file exists
if(argLen == 2 ) and os.path.isfile(sys.argv[1]):
  
    pathToFile = sys.argv[1]
    doc = openFile(pathToFile)
    taskList = doc["tasks"]
    timed = createSchedule(taskList)
    total = addTheRest(taskList,timed)
    total1 = fixNonCompatIssue(total)
    printSchedule(total1)
   
else:
    print(usage)

