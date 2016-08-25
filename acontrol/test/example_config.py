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
    "modes": ["lba_inner", "lba_outer"],
    "subbands": [
      318,
      319,
      321,
      322,
      323,
      324,
      325,
      326,
      310,
      311,
      312,
      313,
      314,
      315,
      316,
      317
    ]
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
          "name": "ais002-1",
          "address": "10.195.100.30:45001"
        },
        {
          "name": "ais002-2",
          "address": "10.195.100.30:45002"
        },
        {
          "name": "ais002-3",
          "address": "10.195.100.30:45003"
        },
        {
          "name": "ais003-1",
          "address": "10.195.100.40:45001"
        },
        {
          "name": "ais003-2",
          "address": "10.195.100.40:45002"
        },
        {
          "name": "ais003-3",
          "address": "10.195.100.40:45003"
        },
        {
          "name": "ais004-1",
          "address": "10.195.100.50:45001"
        },
        {
          "name": "ais004-2",
          "address": "10.195.100.50:45002"
        },
        {
          "name": "ais004-3",
          "address": "10.195.100.50:45003"
        },
        {
          "name": "ais005-1",
          "address": "10.195.100.60:45001"
        },
        {
          "name": "ais005-2",
          "address": "10.195.100.60:45002"
        },
        {
          "name": "ais005-3",
          "address": "10.195.100.60:45003"
        },
        {
          "name": "ais006-1",
          "address": "10.195.100.70:45001"
        },
        {
          "name": "ais006-2",
          "address": "10.195.100.70:45002"
        },
        {
          "name": "ais007-1",
          "address": "10.195.100.80:45001"
        },
        {
          "name": "ais007-2",
          "address": "10.195.100.80:45002"
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
          "address": "127.0.0.1:5000"
        },
        {
          "name": "p1",
          "address": "127.0.0.1:5001"
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
