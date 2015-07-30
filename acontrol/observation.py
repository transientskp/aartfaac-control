from acontrol.parset import Parset

class Observation(object):
    """
    Encapsulates a LOFAR observation.
    """
    def __init__(self, filepath):
        self.parset = filepath
        self.filepath = filepath
        p = Parset(self.filepath)
        self.start_time    = p.getDateTime("ObsSW.Observation.startTime")
        self.end_time      = p.getDateTime("ObsSW.Observation.stopTime")
        self.antenna_array = p.getString("ObsSW.Observation.antennaArray")
        self.antenna_set   = p.getString("ObsSW.Observation.antennaSet")
        self.stations      = p.getString("ObsSW.Observation.ObservationControl.StationControl._hostname")[1:-1].split(',');
        self.sample_clock  = p.getInt("ObsSW.Observation.sampleClock")
        # self.valid = p.getString("Observation.ObservationControl.StationControl.aartfaacPiggybackAllowed") == "true"
        self.valid = True; # NOTE: Currently ignoring the piggyback flag for testing. TODO: Remove before production use.
        self.bandfilter = p.getString ("ObsSW.Observation.bandFilter")
        # Set the default parameters for AARTFAAC. These will be overwritten by the 
        # AARTFAAC parset parser. These are arbitrary defaults.
        self.subbands              =  '100,150,200,250,300,350,400,450';
        self.aartfaac_stations     = ['cs002c', 'cs003c', 'cs004c', 'cs005c', 'cs006c', 'cs007c'];
        self.aartfaac_arrayconfigs = ['LBA_OUTER', 'LBA_INNER', 'HBA_DUAL', 'HBA_JOINED', 'HBA_DUAL_INNER'];
        self.start_subband = int(self.subbands.split(',')[0]);

        # See http://www.astron.nl/radio-observatory/astronomers/users/technical-information/frequency-selection/station-clocks-and-rcu for explanation of this conversion.
        if (self.bandfilter == "LBA_30_90" or self.bandfilter == "LBA_10_90"):
            self.nyquistzone = 1;

        elif (self.bandfilter == "HBA_110_190"):
            self.nyquistzone = 2;

        elif (self.bandfilter == "HBA_170_230" or self.bandfilter == "HBA_210_250"):
            self.nyquistzone = 3;

        self.start_freq = self.start_subband*self.sample_clock*1e6/1024.0
        self.chan_width = self.sample_clock*1e6/(64.0*1024.0)

    # See http://www.astron.nl/radio-observatory/astronomers/users/technical-information/frequency-selection/station-clocks-and-rcu for explanation of this conversion.
    def subband2freq (self, subband):
        # NOTE: Sample clock in returned in MHz. 512 is hardcoded as the PFB taps.
        print 'nzone: %d, subband: %d, samp_clk:%d' % (self.nyquistzone, subband, self.sample_clock);
        return ((self.nyquistzone - 1 + subband/512.)*self.sample_clock*1e6/2.); 
        
    def save(self, filepath):
      self.parset.writeFile(filepath)

    @property
    def duration(self):
        return (self.end_time - self.start_time).seconds

    @property
    def start(self):
        return self.start_time.strftime("%H:%M")

    @property
    def end(self):
        return self.end_time.strftime("%H:%M")

    # Returns true if ALL aartfaac-6 stations were found in the observation
    @property
    def is_aartfaac (self):
        return set(self.aartfaac_stations).issubset (self.stations);

    def is_valid(self):
        print '<-- Observation antennaset = %s, duration = %dsec, is_aartfaac = %s.' % (self.antenna_set, self.duration, self.is_aartfaac);
        return self.valid and self.is_aartfaac and set(self.antenna_set).issubset(self.aartfaac_arrayconfig) and (self.duration > 600);

    def __str__(self):
        return "[OBS - %s %0.1fMHz %s-%s] %s" % (self.antenna_set, self.start_freq*1e-6, self.start, self.end, self.filepath)

    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
