#!/usr/bin/env python3

import time
import datetime


def GenerateNewCerts(workQueue):
    pass


def getYearMap(quantum, lead):
    returns = []

    # Let's enforce some limits (somewhat arbitrary)

    if quantum > 1.0:
        quantum = 1.0    # for now not allowing greater than 1 year
    if quantum < .05:
        quantum = .05    # Year into 20 slices

    if lead < .1:
        lead = .1
    if lead > 5:
        lead = 5

    # Compute real lead - how many years do we need to concern ourselves with
    rLead = int(float(lead)+.5)+1
    if rLead < 1:
        rLead = 1

    # Don't process certs requests starting after this date
    endFrame = datetime.datetime.fromtimestamp(time.time() + (366*lead*86400))
    #print("EndFrame=", endFrame)

    thisYear = datetime.date.fromtimestamp(time.time())

    # loop through all possible years
    for endYear in range(0, rLead):
        start = datetime.datetime(thisYear.year+endYear, 1, 1)
        end = datetime.datetime(thisYear.year+endYear+1, 1, 1)

        # Compute from quantum the number of slices to make of year

        delta = (end - start).days   # days in year
        interval = int(1.0 / quantum)   # number of slices in a year

        days = int(delta / interval)   # Number of days in a slice
        last = int(delta % interval)   # Remainder for last slice

        # print("This: ", start, end, delta, interval, days, last)

        # generate the slices
        for i in range(0, interval):
            startInterval = start + datetime.timedelta(days=i*days)
            if i < (interval - 1):
                endInterval = startInterval + datetime.timedelta(days=days)
            else:
                endInterval = startInterval + \
                    datetime.timedelta(
                        days=days+last)   # add the remainder for last slice

            if endInterval < datetime.datetime.now():
                continue   # We never make certificates in the past

            if startInterval > endFrame:
                continue   # Don't make the certs after the lead time

            #print("   ", startInterval, endInterval)
            returns.append(startInterval)
            returns.append(endInterval)

    return returns


def checkExistingCert(certificates, start, end):
    return start, end, 0


def CreateCertificates(certificates, cType, name, quantum, load, lead, existing, s, e):
    print("Create: "+cType+"/"+name, load-existing,s,e)
    pass


def FindCertificates(cType, name,  certificates, quantum, load, lead):
    # Compute the slice map from the quantum and the lead-time
  
    sliceMap = getYearMap(quantum, lead)
    # print(sliceMap)

    for i in range(0,len(sliceMap),2):
        sliceStart = sliceMap[i]
        sliceEnd = sliceMap[i+1]

        s, e, existing = checkExistingCert(certificates, sliceStart, sliceEnd)

        if s == None:
            continue

        CreateCertificates(certificates, cType, name, quantum,
                          load, lead, existing, s, e)
