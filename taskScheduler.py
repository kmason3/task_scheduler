#! /usr/bin/python

import yaml
import json, operator, datetime

with open(r'C:\Users\masonk\Downloads\tasks_to_complete.yml', 'r') as stream:
    try:
        doc = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

def sortByDuration(taskList):
    return sorted(taskList, key=operator.itemgetter('duration'))

def sortByDurationRev(taskList):
    return sorted(taskList, key=operator.itemgetter('duration'),reverse=True)

def sortByStart(taskList):
    return sorted(taskList, key=operator.itemgetter('start'))

def sortByEnd(taskList):
    return sorted(taskList, key=operator.itemgetter('end'))

def sortFinal(taskList):
    k = 0
    for task in range(1,len(taskList)):
        if taskList[k]['startTime'] == taskList[task]['startTime'] :
            print(taskList[k]['description'] + ' ' + taskList[task]['description'])
            temp = taskList[k]
            taskList[k] = taskList[task]
            taskList[task] = temp
            k=task
    return taskList


def tasksWithTimes(taskList):
    nonNullList=[]
    for task in taskList:
        if task['start'] != None:
            nonNullList.append(task)
            task['timeCondition'] = True        
    nonNullList = sortByStart(nonNullList)
    return nonNullList

def taskToBeTimed(taskList):
    nullList=[]
    for task in taskList:
        if task['start'] == None:
            nullList.append(task)
            task['timeCondition'] = False
    nullList = sortByDuration(nullList)        
    return nullList

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

def compatable(task1, task2):
    task1Id = task1["id"]
    task2CompList = task2["compatibility"]
    if task2CompList == None or task1Id == None:
        return False
    if task1Id in task2CompList:
        return True
    else:
        return False

def calcLeastEndTime(task1, task2):
    if task1["endTime"] < task2["endTime"]:
        return task1["end"]
    elif task2["endTime"] < task1["endTime"]:
        return task2["end"]
def calcGreaterEndTime(task1, task2):
    if task1["endTime"] > task2["endTime"]:
        return task1["end"]
    elif task2["endTime"] > task1["endTime"]:
        return task2["end"]

def taskWithLeastEndTime(task1,task2):
    if task1["endTime"] < task2["endTime"]:
        return task1
    else:
        return task2

def taskWithGreaterEndTime(task1,task2):
    if task1["endTime"] > task2["endTime"]:
        return task1
    else:
        return task2

def calcDifInStarts(task1, task2):
    return task2["startTime"] - task1["startTime"]

def calcDurTime(task):
    dur = task["duration"]
    return datetime.timedelta(minutes=dur)

def calcStartTime(task):
    startTime = task["start"]
    return datetime.datetime.strptime(startTime, '%H:%M')
    
def calcEndTime(task):
    startAsTime = calcStartTime(task)
    dur = task["duration"]
    endAsTime = startAsTime + datetime.timedelta(minutes=dur) 
    return endAsTime

def calcEnd(task):
    endAsTime = calcEndTime(task)
    return datetime.datetime.strftime(endAsTime,'%H:%M')

def assignDurTime(task):
    durTime = calcDurTime(task)
    task['durTime'] = durTime

def printSchedule(taskList):
    taskList = sortByEnd(taskList)
    taskList = sortByStart(taskList)
    for task in taskList:
        print(task['description'] + ','+ task["start"] + ' ' + task['end'])

def timeIsBetween(startTime,endTime,timeToCheck):
    if startTime < endTime:
        return timeToCheck > startTime and timeToCheck < endTime

def createSchedule(taskList):
    timed = tasksWithTimes(taskList)
    assignTimesToDict(timed)
    unTimed = taskToBeTimed(taskList)
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


######## Main Testing ########

numOfTasks = len(doc["tasks"])
origList = doc["tasks"]
timed = createSchedule(origList)
# origList1 = sortByDurationRev(origList)
total = addTheRest(origList,timed)
total1 = fixNonCompatIssue(total)
printSchedule(total1)
# print('\n')
# total2 = sortFinal(total1)
# printSchedule(total2)
# print('\n')
# total3 = sortByEnd(total1)
# printSchedule(total3)
# print('\n')
# total4 = sortByStart(total3)
# printSchedule(total4)