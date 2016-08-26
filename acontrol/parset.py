import time
import datetime

class Parset(dict):
    """
    A pure Python parameterset parser.

    Original version by Gijs Molenaar for LOFAR Transients Pipeline.
    """
    def __init__(self, filename=None):
        """Create a parameterset object."""
        self.filename = filename
        if filename:
            self.adoptFile(filename)

    def _parse_file(self, filename):
        f = open(filename)
        for line in f:
            if '#' in line:
                line = line.split('#')[0]
            if '=' in line:
                key, value = line.split('=', 1)
                self[key.strip()] = value.strip()
        f.close()

    def adoptFile(self, filename):
        """Supplement this parset with the contents of filename."""
        self._parse_file(filename)

    def getBool(self, key, default=None):
        return bool(self.get(key, default))

    def getFloat(self, key, default=None):
        return float(self.get(key, default))

    def getInt(self, key, default=None):
        return int(self.get(key, default))

    def getString(self, key, default=None):
        return str(self.get(key, default))

    def keywords(self):
        return self.keys()

    def remove(self, key):
        self.pop(key)

    def replace(self, key, value):
        self[key] = value

    def writeFile(self, filename):
        file = open(filename, 'w')
        items = self.items()
        items.sort()
        for k,v in items:
          file.write("%s=%s\n" % (k, v))
        file.close()

    def getDateTime(self, key, formatstring="%Y-%m-%d %H:%M:%S"):
        """
        Return the value of key as an instance of datetime.datetime.
        """
        ts = time.strptime(self.get(key), formatstring)
        return datetime.datetime(
            ts.tm_year, ts.tm_mon, ts.tm_mday, ts.tm_hour, ts.tm_min, ts.tm_sec
        )
