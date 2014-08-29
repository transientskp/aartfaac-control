import time
import datetime

class Parset(dict):
    """
    A pure Python parameterset parser.

    Original version by Gijs Molenaar for LOFAR Transients Pipeline.
    """
    def __init__(self, filename=None):
        """Create a parameterset object."""
        if filename:
            self.adoptFile(filename)

    def _parse_file(self, filename):
        self._data = {}
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

    def getVector(self, key):
        """Get the value as a vector of values."""
        return [self[key]]

    def getRecord(self, key):
        """Get the value as a record."""
        return self[key]

    def getBoolVector(self, key, default=None, expandable=False):
        """
        Get the value as a list of boolean values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.

        """
        if expandable:
            raise NotImplementedError
        return [bool(self.get(key, default))]

    def getIntVector(self, key, default=None, expandable=False):
        """
        Get the value as a list of integer values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.

        """
        if expandable:
            raise NotImplementedError
        return [int(self.get(key, default))]

    def getFloatVector(self, key, default=None, expandable=False):
        """
        Get the value as a list of floating point values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.
        """
        if expandable:
            raise NotImplementedError
        return [float(self.get(key, default))]

    def getDoubleVector(self, key, default=None, expandable=False):
        """
        Get the value as a list of floating point values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.

        """
        if expandable:
            raise NotImplementedError
        return [float(self.get(key, default))]

    def getStringVector(self, key, default=None, expandable=False):
        """
        Get the value as a list of string values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.

        """
        if expandable:
            raise NotImplementedError
        return [str(self.get(key, default))]

    def fullModuleName(self):
        raise NotImplementedError

    def getBool(self, key, default=None):
        return bool(self.get(key, default))

    def getDouble(self, key, default=None):
        return float(self.get(key, default))

    def getFloat(self, key, default=None):
        return float(self.get(key, default))

    def getInt(self, key, default=None):
        return int(self.get(key, default))

    def getString(self, key, default=None):
        return str(self.get(key, default))

    def isDefined(self, key):
        return key in self._data

    def keywords(self):
        return self.keys()

    def remove(self, key):
        self.pop(key)

    def replace(self, key, value):
        self[key] = value

    def size(self):
        return len(self._data)

    def locateModule(self):
        raise NotImplementedError

    def subtractSubset(self):
        raise NotImplementedError

    def version(self):
        raise NotImplementedError

    def writeFile(self, filename):
        file = open(filename, 'w')
        items = self.items()
        items.sort()
        for k,v in items:
          file.write("%s=%s\n" % (k, v))
        file.close()

    def isRecord(self):
        raise NotImplementedError

    def isVector(self):
        raise NotImplementedError

    def __reduce__(self):
        raise NotImplementedError

    def getDateTime(self, key, formatstring="%Y-%m-%d %H:%M:%S"):
        """
        Return the value of key as an instance of datetime.datetime.
        """
        ts = time.strptime(self.get(key), formatstring)
        return datetime.datetime(
            ts.tm_year, ts.tm_mon, ts.tm_mday, ts.tm_hour, ts.tm_min, ts.tm_sec
        )
