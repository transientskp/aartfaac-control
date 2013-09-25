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
