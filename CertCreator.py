#!/usr/bin/env python3

import time
import datetime


def GenerateNewCerts(workQueue):
    pass


def getYearMap(quantum, lead):
    returns = []

    # Let's enforce some limits (somewhat arbitrary)

    if quantum > 1.0:
        quantum = 1.0    # for now
    if quantum < .05:
        quantum = .05

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

    for endYear in range(0, rLead):
        start = datetime.datetime(thisYear.year+endYear, 1, 1)
        end = datetime.datetime(thisYear.year+endYear+1, 1, 1)

        delta = (end - start).days
        interval = int(1.0 / quantum)

        days = int(delta / interval)
        last = int(delta % interval)

        # print("This: ", start, end, delta, interval, days, last)

        for i in range(0, interval):
            startInterval = start + datetime.timedelta(days=i*days)
            if i < (interval - 1):
                endInterval = startInterval + datetime.timedelta(days=days)
            else:
                endInterval = startInterval + \
                    datetime.timedelta(days=days+last)

            if endInterval < datetime.datetime.now():
                continue

            if startInterval > endFrame:   # not the whole year
                continue

            #print("   ", startInterval, endInterval)
            returns.append(startInterval)
            returns.append(endInterval)

    return returns


def FindCertificates(cType, name,  certificates, quantum, load, lead):
    yearMap = getYearMap(quantum, lead)
