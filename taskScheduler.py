#! /usr/bin/python

import yaml
import json, operator, datetime

with open(r'C:\Users\masonk\Downloads\tasks_to_complete.yml', 'r') as steam:
    try:
        doc = yaml.load(steam)
    except yaml.YAMLError as exc:
        print(exc)

def sortByDuration(taskList):
    return sorted(taskList, key=operator.itemgetter('duration'))

def sortByStart(taskList):
    return sorted(taskList, key=operator.itemgetter('start'))

def sortByEnd(taskList):
    return sorted(taskList, key=operator.itemgetter('end'))

def tasksWithTimes(taskList):
    nonNullList=[]
    for task in taskList:
        if task['start'] != None:
            nonNullList.append(task)        
    nonNullList = sortByStart(nonNullList)
    return nonNullList

def taskToBeTimed(taskList):
    nullList=[]
    for task in taskList:
        if task['start'] == None:
            nullList.append(task)
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

    if task1Id in task2CompList:
        return True
    else:
        return False

def calcLeastEndTime(task1, task2):
    if task1["endTime"] < task2["endTime"]:
        return task1["end"]
    else:
        return task2["end"]

def taskWithLeastEndTime(task1,task2):
    if task1["endTime"] < task2["endTime"]:
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
    for task in taskList:
        print(task['description'] + ','+ task["start"] + ' ' + task['end'])

# def overlap(task1,task2):

def createSchedule(taskList):
    timed = tasksWithTimes(taskList)
    assignTimesToDict(timed)
    unTimed = taskToBeTimed(taskList)
    tasks = timed + unTimed
    mindur = unTimed[0]['duration']
    A = []
    k = 0
    j=0
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
           printSchedule(A)

## Main Testing ##

numOfTasks = len(doc["tasks"])
origList = doc["tasks"]
createSchedule(origList)
# timed = tasksWithTimes(origList)
# timed = addTimesToDict(timed)
# difStart = calcDifInStarts(timed[0], timed[1])
# # print(calcEnd(timed[0]))