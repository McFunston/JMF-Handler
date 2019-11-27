#!/usr/bin/env python3
# Tool for extracting a list of jobs from a "QueryQueueStatus" JMF response
# Tested with Prinect, but should work with any JDF/JMF Device that has a queue

import xml.etree.ElementTree as et
import sys
import csv
import requests
from os import listdir
from os.path import isfile, isdir, join

""" def GetQueueStatus(url):
    #Returns a GetQueueStatus response from an active JMF server
    headers = {'content-type': 'application/vnd.cip4-jmf+xml'}
    qs = '<JMF xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" SenderID="org.cip4.tools.controller" TimeStamp="2004-08-30T17:23:00+01:00" Version="1.2"> <Query ID="Q1000" Type="QueueStatus" xsi:type="QueryQueueStatus"/> </JMF>'
    status = requests.post(url, data=qs, headers=headers)
    with open ('qs.jmf', 'w') as jmffile:
        jmffile.write(status.text)
    return status.text """

def GetQueueStatus(url):
    #Returns a GetQueueStatus response from an active JMF server
    headers = {'content-type': 'application/vnd.cip4-jmf+xml'}
    qs = '<JMF xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" SenderID="org.cip4.tools.controller" TimeStamp="2004-08-30T17:23:00+01:00" Version="1.2"> <Query ID="Q1000" Type="QueueStatus" xsi:type="QueryQueueStatus"/> </JMF>'
    status = requests.post(url, data=qs, headers=headers)
    return status.text

def GetQueue(tree):
    #Returns a dictionary of QueueEntry(s) from a 'QueueStatus' response    
    root = tree.getroot()    
    return root.findall('{http://www.CIP4.org/JDFSchema_1_1}Response/{http://www.CIP4.org/JDFSchema_1_1}Queue/{http://www.CIP4.org/JDFSchema_1_1}QueueEntry')

def GetQSFromURL(url):
    tree = et.ElementTree(et.fromstring(GetQueueStatus(url)))
    return tree

def GetQSFromFile(JMFFile):
    tree = et.parse(JMFFile)
    return tree

def JMFQueueToCSV(JMF, CSV):
    # Converts a JMF 'QueueStatus' response to a CSV file - The CSV columns will be in random order since it converts from a dictionary
    Queue = GetQueue(JMF)
    
    with open(CSV, 'w', newline='') as csvfile:
        all_keys = set().union(*(d.keys() for d in Queue)) #get all possible keys
        writer = csv.DictWriter(csvfile, fieldnames=all_keys)
        writer.writeheader()
        for QueueEntry in Queue:
            writer.writerow(QueueEntry.attrib)

def JMFQueueToJobList(tree):
    queueJobList = list()
    Queue = GetQueue(tree)
    for QueueEntry in Queue:
        if QueueEntry.attrib['StatusDetails'] != 'Finished':
            queueJobList.append(QueueEntry.attrib['QueueEntryID'])
    return queueJobList

# def GetJMFCommand(JMF):
#     tree = et.parse(JMF)
#     root = tree.getroot()
#     return root

# def ModJMFCommand(jmf, value):
#     tree = et.parse(jmf)
#     root = tree.getroot()
#     entry = root.findall('{http://www.CIP4.org/JDFSchema_1_1}'+'Command/{http://www.CIP4.org/JDFSchema_1_1}QueueEntryDef')
#     entry[0].attrib['QueueEntryID'] = value
#     return tree

def CloseJob(job):
    headers = {'content-type': 'application/vnd.cip4-jmf+xml'}
    modjmf = '<?xml version="1.0" encoding="UTF-8"?> <JMF xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" SenderID="CIP4 Alces Bologna-18.03" TimeStamp="2019-11-26T13:05:25-05:00" Version="1.3"> <Command ID="ALCES_622MXD_4_20191126130525" Type="AbortQueueEntry" xsi:type="CommandAbortQueueEntry"> <QueueEntryDef QueueEntryID="'+job+'" /> </Command> </JMF>'    
    status = requests.post('http://kansw286:8889/jmfportal?', data=modjmf, headers=headers)
    print(status.text)


def get_folder_list(path):
    """Given a path returns a list of all folders contained,
    path -- Path that you want to get the file list from
    Returns list of string (folder names)"""
    try:
        folder_list = [f for f in listdir(path) if isdir(join(path, f))]
        return folder_list
    except FileNotFoundError:
        print("Failure in get_folder_list" + path)
        return

def get_archive_list(path):
    folderList = get_folder_list(path)
    archiveList = list()
    for folder in folderList:
        if len(folder) >= 5:
            if 'FSC_' in folder:
                job = folder[-5:]
            else: 
                job = folder[:5]
        archiveList.append(job)
    return archiveList

#JMFQueueToCSV("qs.jmf", "jobs.csv")
#qs = GetQueueStatus('http://kansw286:8889/jmfportal?')
#qs = GetQSFromFile('TestData/Jobs.JMF')
# print(qs)
# CloseJob('FloorPlan')

def FinishJob(url, path):
    queueList = JMFQueueToJobList(GetQSFromURL(url))
    archiveList = get_archive_list(path)
    for j in queueList:
        for archive in archiveList:
            if archive in j:
                CloseJob(j)

# FinishJob('http://kansw286:8889/jmfportal?','/Volumes/WIP2/To_Archive')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Arguments 'url', 'path' required")
    else:
        FinishJob(sys.argv[1], sys.argv[2])