#!/usr/bin/env python3
# Tool for extracting a list of jobs from a "QueryQueueStatus" JMF response
# Tested with Prinect, but should work with any JDF/JMF Device that has a queue

import xml.etree.ElementTree as et
import sys
import csv

def ListJobs(JMF, CSV):
    tree = et.parse(JMF)
    root = tree.getroot()
    
    Queue = root.findall('{http://www.CIP4.org/JDFSchema_1_1}Response/{http://www.CIP4.org/JDFSchema_1_1}Queue/{http://www.CIP4.org/JDFSchema_1_1}QueueEntry')
    
    with open(CSV, 'w', newline='') as csvfile:
        fn = Queue[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=Queue[0].keys())
        writer.writeheader()
        for QueueEntry in Queue:
            writer.writerow(QueueEntry.attrib)
            print(QueueEntry.attrib['QueueEntryID'])


    print('test')

ListJobs("TestData/Jobs.JMF", "jobs.csv")

""" if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Arguments 'JMF File', 'CSV File' required")
    else:
        ListJobs(sys.argv[1], sys.argv[2]) """