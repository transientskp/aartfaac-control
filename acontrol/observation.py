from acontrol.parset import Parset

class Observation(object):
    """
    Encapsulates a LOFAR observation.
    """
    def __init__(self, filepath):
        self.parset = filepath
        self.filepath = filepath
        p = Parset(self.filepath)
        self.start_time = p.getDateTime("Observation.startTime")
        self.end_time = p.getDateTime("Observation.stopTime")
        self.antenna_array = p.getString("Observation.antennaArray")
        self.antenna_set = p.getString("Observation.antennaSet")
        self.sample_clock = p.getInt("Observation.sampleClock")
        self.valid = p.getString("Observation.ObservationControl.StationControl.aartfaacPiggybackAllowed") == "true"
        self.start_subband = 590/2
        self.start_freq = self.start_subband*self.sample_clock*1e6/1024.0
        self.chan_width = self.sample_clock*1e6/(64.0*1024.0)

    def save(self, filepath):
      self.parset.writeFile(filepath)

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def start(self):
        return self.start_time.strftime("%Y%m%d-%H%M%S")

    # TODO: Check for aartfaac piggyback flag
    def is_valid(self):
        return self.valid and self.antenna_array == "LBA"

    def __str__(self):
        return "OBS - %s %0.1fMHz [%s]" % (self.antenna_set, self.start_freq*1e-6, self.filepath)

    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
