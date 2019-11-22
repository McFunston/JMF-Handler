#!/usr/bin/env python3
# Tool for extracting a list of jobs from a "QueryQueueStatus" JMF response
# Tested with Prinect, but should work with any JDF/JMF Device that has a queue

import xml.etree.ElementTree as et
import sys
import csv

def GetQueue(JMF):
    #Returns a dictionary of QueueEntry(s) from a 'QueueStatus' response
    tree = et.parse(JMF)
    root = tree.getroot()
    
    return root.findall('{http://www.CIP4.org/JDFSchema_1_1}Response/{http://www.CIP4.org/JDFSchema_1_1}Queue/{http://www.CIP4.org/JDFSchema_1_1}QueueEntry')

def JMFQueueToCSV(JMF, CSV):
    # Converts a JMF 'QueueStatus' response to a CSV file - The CSV columns will be in random order since it converts from a dictionary
    Queue = GetQueue(JMF)
    
    with open(CSV, 'w', newline='') as csvfile:
        all_keys = set().union(*(d.keys() for d in Queue)) #get all possible keys
        writer = csv.DictWriter(csvfile, fieldnames=all_keys)
        writer.writeheader()
        for QueueEntry in Queue:
            writer.writerow(QueueEntry.attrib)

JMFQueueToCSV("TestData/Jobs.JMF", "jobs.csv")

""" if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Arguments 'JMF File', 'CSV File' required")
    else:
        ListJobs(sys.argv[1], sys.argv[2]) """