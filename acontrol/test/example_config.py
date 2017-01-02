import unittest
import textwrap
import tempfile

EXAMPLE_CONFIG = """
{
  "starttime": "now",
  "email": [
    "folkerthuizinga@gmail.com",
    "hsuyeep@gmail.com",
    "antonia.rowlinson@gmail.com",
    "mk.kuiack@gmail.com"
  ],
  "lba": {
    "modes": ["lba_inner", "lba_outer"]
  },
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
    "atv": {
      "name": "aartfaac-tv",
      "address": "10.144.6.13:45001",
      "input": "10.195.100.20:4000",
      "argv": {
        "port": 5000,
        "subband": 313
      }
    },
    "pipelines": {
      "argv": {
        "antsigma": 4,
        "vissigma": 2.5,
        "buffer": 70,
        "nthreads": 6,
        "v": 1
      },
      "instances": [
        {
          "name": "ais002-2",
          "address": "10.195.100.30:45002",
          "input": "10.195.100.30:4001",
          "argv": {
            "subband": 314
          }
        },
        {
          "name": "ais002-3",
          "address": "10.195.100.30:45003",
          "input": "10.195.100.30:4002",
          "argv": {
            "subband": 315
          }
        },
        {
          "name": "ais003-1",
          "address": "10.144.6.16:45001",
          "input": "10.195.100.40:4000",
          "argv": {
            "subband": 316
          }
        },
        {
          "name": "ais003-2",
          "address": "10.144.6.16:45002",
          "input": "10.195.100.40:4001",
          "argv": {
            "subband": 317
          }
        },
        {
          "name": "ais003-3",
          "address": "10.144.6.16:45003",
          "input": "10.195.100.40:4002",
          "argv": {
            "subband": 318
          }
        },
        {
          "name": "ais004-1",
          "address": "10.144.6.17:45001",
          "input": "10.195.100.50:4000",
          "argv": {
            "subband": 319
          }
        },
        {
          "name": "ais004-2",
          "address": "10.144.6.17:45002",
          "input": "10.195.100.50:4001",
          "argv": {
            "subband": 320
          }
        },
        {
          "name": "ais004-3",
          "address": "10.144.6.17:45003",
          "input": "10.195.100.50:4002",
          "argv": {
            "subband": 295
          }
        },
        {
          "name": "ais005-1",
          "address": "10.144.6.18:45001",
          "input": "10.195.100.60:4000",
          "argv": {
            "subband": 296
          }
        },
        {
          "name": "ais005-2",
          "address": "10.144.6.18:45002",
          "input": "10.195.100.60:4001",
          "argv": {
            "subband": 297
          }
        },
        {
          "name": "ais005-3",
          "address": "10.144.6.18:45003",
          "input": "10.195.100.60:4002",
          "argv": {
            "subband": 298
          }
        },
        {
          "name": "ais006-1",
          "address": "10.144.6.19:45001",
          "input": "10.195.100.70:4000",
          "argv": {
            "subband": 299
          }
        },
        {
          "name": "ais006-2",
          "address": "10.144.6.19:45002",
          "input": "10.195.100.70:4001",
          "argv": {
            "subband": 300
          }
        },
        {
          "name": "ais007-1",
          "address": "10.144.6.20:45001",
          "input": "10.195.100.80:4000",
          "argv": {
            "subband": 301
          }
        },
        {
          "name": "ais007-2",
          "address": "10.144.6.20:45002",
          "input": "10.195.100.80:4001",
          "argv": {
            "subband": 302
          }
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
