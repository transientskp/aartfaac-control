from acontrol.parset import Parset
import datetime

class Observation(object):
    """
    Encapsulates a LOFAR observation.
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.parset = Parset(self.filepath)
        self.start_time = self.parset.getDateTime("Observation.startTime")
        self.end_time = self.parset.getDateTime("Observation.stopTime")
        self.antenna_array = self.parset.getString("Observation.antennaArray")
        self.antenna_set = self.parset.getString("Observation.antennaSet")
        self.sample_clock = self.parset.getInt("Observation.sampleClock")
        self.valid = self.parset.getString("Observation.ObservationControl.StationControl.aartfaacPiggybackAllowed") == "true"

    def save(self, filepath):
      self.parset.writeFile(filepath)

    @property
    def duration(self):
        start_time = self.start_time
        if self.end_time > datetime.datetime.now():
            start_time = max(self.start_time, datetime.datetime.now())
        return (self.end_time - start_time).seconds

    @property
    def start(self):
        return self.start_time.strftime("%H:%M")

    @property
    def end(self):
        return self.end_time.strftime("%H:%M")

    # TODO: Check for aartfaac piggyback flag
    def is_valid(self):
        return self.valid and self.antenna_array == "LBA"

    def __str__(self):
        return "OBS - %s (%s)" % (self.antenna_set, (self.end_time-self.start_time))

    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
