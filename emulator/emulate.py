#!/usr/bin/python

import os, sys
import random
import time
import datetime

sys.path.append(os.path.abspath('acontrol'))
from parset import Parset

if __name__ == "__main__":
  p = Parset('data/Observation201616')
  starttime = datetime.datetime.now()

  i = 0
  while True:
    seconds = random.randint(5, 60)
    starttime += datetime.timedelta(0, seconds)

    seconds = random.randint(10, 30)
    endtime = starttime + datetime.timedelta(0, seconds)

    filename = 'Observation%06d' % (i)

    p.replace('ObsSW.Observation.startTime', starttime.strftime("%Y-%m-%d %H:%M:%S"))
    p.replace('ObsSW.Observation.endTime', endtime.strftime("%Y-%m-%d %H:%M:%S"))
    p.writeFile('data/%s' % (filename))

    i += 1
    seconds = (endtime - datetime.datetime.now()).seconds + 2
    print "Written %s to disk, sleeping %d seconds" % (filename, seconds)
    print "   starttime %s" % (starttime)
    print "   endtime   %s" % (endtime)
    time.sleep(seconds)
