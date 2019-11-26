#!/usr/bin/env python3
# Tool for extracting a list of jobs from a "QueryQueueStatus" JMF response
# Tested with Prinect, but should work with any JDF/JMF Device that has a queue

import xml.etree.ElementTree as et
import sys
import csv
import pip._vendor.requests as requests

def GetQueueStatus(url):
    #Returns a GetQueueStatus response from an active JMF server
    headers = {'content-type': 'application/vnd.cip4-jmf+xml'}
    qs = '<JMF xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" SenderID="org.cip4.tools.controller" TimeStamp="2004-08-30T17:23:00+01:00" Version="1.2"> <Query ID="Q1000" Type="QueueStatus" xsi:type="QueryQueueStatus"/> </JMF>'
    status = requests.post(url, data=qs, headers=headers)
    with open ('qs.jmf', 'w') as jmffile:
        jmffile.write(status.text)
    return status.text

def GetQueue(JMF):
    #Returns a dictionary of QueueEntry(s) from a 'QueueStatus' response
    tree = et.parse(JMF)
    root = tree.getroot()    
    return root.findall('{http://www.CIP4.org/JDFSchema_1_1}Response/{http://www.CIP4.org/JDFSchema_1_1}Queue/{http://www.CIP4.org/JDFSchema_1_1}QueueEntry')

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

JMFQueueToCSV("qs.jmf", "jobs.csv")
#qs = GetQueueStatus('http://kansw286:8889/jmfportal?')
#qs = GetQSFromFile('TestData/Jobs.JMF')
# print(qs)

""" if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Arguments 'JMF File', 'CSV File' required")
    else:
        ListJobs(sys.argv[1], sys.argv[2]) """