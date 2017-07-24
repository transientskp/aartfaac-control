import unittest
import textwrap
import tempfile

EXAMPLE_CONFIG = """
{
  "starttime": "now",
  "email": [
    "folkerthuizinga@gmail.com",
    "antonia.rowlinson@gmail.com",
    "mk.kuiack@gmail.com",
    "hsuyeep@gmail.com"
  ],
  "lba": {
    "modes": ["lba_inner", "lba_outer", "lba_sparse_even", "lba_sparse_odd"]
  },
  "bitmode": 16,
  "subbands": ["200","201","202","203","204","205","206","207",
               "224","225","226","227","228","229","230","231"],
  "programs": {
    "correlators": {
      "argv": {
        "A": "0:6",
        "C": "63",
        "b": "16",
        "d": "0",
        "g": "0-9",
        "m": "9",
        "c": "256",
        "O": "0:4,1:4",
        "n": "288",
        "p": "1",
        "s": "8",
        "t": "768",
        "N": "4-11,28-35/16-23,40-47"
      },
      "instances": [
        {
          "name": "agc001",
          "address": "10.144.6.11:45000",
          "argv": {
            "i": "10.195.100.1:53269,10.195.100.1:53277,10.195.100.1:53285,10.195.100.1:53293,10.195.100.1:53301,10.195.100.1:53309"
          }
        },
        {
          "name": "agc002",
          "address": "10.144.6.31:45000",
          "argv": {
            "i": "10.195.100.3:53268,10.195.100.3:53276,10.195.100.3:53284,10.195.100.3:53292,10.195.100.3:53300,10.195.100.3:53308"
          }
        }
      ]
    },
    "pipelines": {
      "argv": {
        "antsigma": 3.0,
        "vissigma": 2.5,
        "buffer": 60,
        "v": 1
      },
      "instances": [
        {
          "name": "ais002-0",
          "address": "10.144.6.15:45000",
          "input": "10.195.100.30:4000",
          "argv": {
            "affinity": "2,4,6,2"
          }
        },
        {
          "name": "ais002-1",
          "address": "10.144.6.15:45001",
          "input": "10.195.100.30:4001",
          "argv": {
            "affinity": "2,8,10,2"
          }
        },
        {
          "name": "ais002-2",
          "address": "10.144.6.15:45002",
          "input": "10.195.100.30:4002",
          "argv": {
            "affinity": "2,12,14,2"
          }
        },
        {
          "name": "ais003-0",
          "address": "10.144.6.16:45000",
          "input": "10.195.100.40:4000",
          "argv": {
            "affinity": "2,18,20,22,24,26,28,30,2"
          }
        },
        {
          "name": "ais003-1",
          "address": "10.144.6.16:45001",
          "input": "10.195.100.40:4001",
          "argv": {
            "affinity": "2,1,3,2"
          }
        },
        {
          "name": "ais003-2",
          "address": "10.144.6.16:45002",
          "input": "10.195.100.40:4002",
          "argv": {
            "affinity": "2,5,7,2"
          }
        },
        {
          "name": "ais004-0",
          "address": "10.144.6.17:45000",
          "input": "10.195.100.50:4000",
          "argv": {
            "affinity": "2,9,11,2"
          }
        },
        {
          "name": "ais004-1",
          "address": "10.144.6.17:45001",
          "input": "10.195.100.50:4001",
          "argv": {
            "affinity": "2,13,15,2"
          }
        },
        {
          "name": "ais004-2",
          "address": "10.144.6.17:45002",
          "input": "10.195.100.50:4002",
          "argv": {
            "affinity": "2,4,6,2"
          }
        },
        {
          "name": "ais005-0",
          "address": "10.144.6.18:45000",
          "input": "10.195.100.60:4000",
          "argv": {
            "affinity": "2,8,10,2"
          }
        },
        {
          "name": "ais005-1",
          "address": "10.144.6.18:45001",
          "input": "10.195.100.60:4001",
          "argv": {
            "affinity": "2,12,14,2"
          }
        },
        {
          "name": "ais005-2",
          "address": "10.144.6.18:45002",
          "input": "10.195.100.60:4002",
          "argv": {
            "affinity": "2,18,20,22,24,26,28,30,2"
          }
        },
        {
          "name": "ais006-0",
          "address": "10.144.6.19:45000",
          "input": "10.195.100.70:4000",
          "argv": {
            "affinity": "2,1,3,2"
          }
        },
        {
          "name": "ais006-1",
          "address": "10.144.6.19:45001",
          "input": "10.195.100.70:4001",
          "argv": {
            "affinity": "2,5,7,2"
          }
        },
        {
          "name": "ais007-0",
          "address": "10.144.6.20:45000",
          "input": "10.195.100.80:4000",
          "argv": {
            "affinity": "2,9,11,2"
          }
        },
        {
          "name": "ais007-1",
          "address": "10.144.6.20:45001",
          "input": "10.195.100.80:4001",
          "argv": {
            "affinity": "2,13,15,2"
          }
        }
      ]
    },
    "imagers": {
      "argv": {
       "beammodel": "/data/beammodel/beammodel"
      },
      "instances": [
        {
          "name": "ais001-imager",
          "address": "10.144.6.13:45000",
          "input": "10.195.100.20:4000",
          "argv": {
            "affinity": "0,3,0",
            "output" : "dir:/data,srv:9000"
          }
        }
      ]
    },
    "atv": {
      "argv": {
       "secret": "2yw9-vtjt-3jhr-9e64",
       "const": "/home/prasad/soft/src/aartfaac-tv/data/constellations.json"
      },
      "instances": [
        {
          "name": "ais001-atv",
          "address": "10.144.6.13:45001",
          "host": "10.195.100.20",
          "port": "9000"
        }
      ]
    }
  }
}
"""
EXAMPLE_CONFIG = textwrap.dedent(EXAMPLE_CONFIG).strip()

LOCAL_CONFIG = """
{
  "starttime": "now",
  "email": [
    "none@uva.nl"
  ],
  "lba": {
    "modes": ["lba_inner", "lba_outer"],
    "subbands": [
      318,
      319
    ]
  },
  "programs": {
    "correlators": {
      "argv": {
        "A": "0:6",
        "C": "63"
      },
      "instances": [
        {
          "name": "agc001",
          "address": "127.0.0.1:4000",
          "argv": {
            "i": "10.195.100.1:53269"
          }
        },
        {
          "name": "agc002",
          "address": "127.0.0.1:4001",
          "argv": {
            "i": "10.195.100.3:53268"
          }
        }
      ]
    },
    "pipelines": {
      "argv": {
        "nthreads": 6,
        "v": 1
      },
      "instances": [
        {
          "name": "p0",
          "address": "127.0.0.1:5000",
          "input": "127.0.0.1:4000"

        },
        {
          "name": "p1",
          "address": "127.0.0.1:5001",
          "input": "127.0.0.1:4001"

        }
      ]
    }
  }
}
"""
LOCAL_CONFIG = textwrap.dedent(LOCAL_CONFIG).strip()

class TestWithConfig(unittest.TestCase):
    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile(mode='w')
        self.config_file.write(EXAMPLE_CONFIG)
        self.config_file.seek(0)

    def tearDown(self):
        self.config_file.close()
