#!/usr/bin/python

import os, sys
import random
import time
import datetime

TIME_BETWEEN = 10
TIME_DURATION = 60

sys.path.append(os.path.abspath('acontrol'))
from parset import Parset

if __name__ == "__main__":
  p = Parset('data/MCU001:ObservationControl[0]{259133}')
  starttime = datetime.datetime.now()

  i = 0
  while True:
    starttime += datetime.timedelta(0, TIME_BETWEEN)

    endtime = starttime + datetime.timedelta(0, TIME_DURATION)

    filename = 'MCU001:ObservationControl[0]{%06d}' % (i)

    p.replace('ObsSW.Observation.startTime', starttime.strftime("%Y-%m-%d %H:%M:%S"))
    p.replace('ObsSW.Observation.endTime', endtime.strftime("%Y-%m-%d %H:%M:%S"))
    p.writeFile('data/%s' % (filename))

    i += 1
    seconds = (endtime - datetime.datetime.now()).seconds + 2
    print "Written %s to disk, sleeping %d seconds" % (filename, seconds)
    print "   starttime %s" % (starttime)
    print "   endtime   %s" % (endtime)
    for j in range(seconds):
      sys.stdout.write(".")
      sys.stdout.flush()
      time.sleep(1)
    print "\n"
    starttime = endtime
