from acontrol.parset import Parset

class Observation(object):
    """
    Encapsulates a LOFAR observation.
    """
    def __init__(self, parset):
        self.parset = parset
        p = Parset(self.parset)
        self.start_time = p.getDateTime("ObsSW.Observation.startTime")
        self.end_time = p.getDateTime("ObsSW.Observation.stopTime")
        self.antenna_array = p.getString("ObsSW.Observation.antennaArray")
        self.antenna_set = p.getString("ObsSW.Observation.antennaSet")
        self.sample_clock = p.getInt("ObsSW.Observation.sampleClock")
        self.valid = p.getString("Observation.ObservationControl.StationControl.aartfaacPiggybackAllowed") == "true"
        self.start_subband = 590/2
        self.start_freq = self.start_subband*self.sample_clock*1e6/1024.0
        self.chan_width = self.sample_clock*1e6/(64.0*1024.0)

    def save(self, filename):
      self.parset.writeFile(filename)

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
        return "OBS - A:%s F:%f W:%f" % (self.antenna_set, self.start_freq, self.chan_width)

    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
