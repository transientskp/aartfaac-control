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
    "modes": ["lba_inner", "lba_outer", "lba_sparse_even", "lba_sparse_odd"]
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
            "affinity": "2,4,6,2",
            "subband": 313
          }
        },
        {
          "name": "ais002-1",
          "address": "10.144.6.15:45001",
          "input": "10.195.100.30:4001",
          "argv": {
            "affinity": "2,8,10,2",
            "subband": 314
          }
        },
        {
          "name": "ais002-2",
          "address": "10.144.6.15:45002",
          "input": "10.195.100.30:4002",
          "argv": {
            "affinity": "2,12,14,2",
            "subband": 315
          }
        },
        {
          "name": "ais002-3",
          "address": "10.144.6.15:45003",
          "input": "10.195.100.30:4003",
          "argv": {
            "affinity": "2,18,20,22,24,26,28,30,2",
            "subband": 316
          }
        },
        {
          "name": "ais002-4",
          "address": "10.144.6.15:45004",
          "input": "10.195.100.30:4004",
          "argv": {
            "affinity": "2,1,3,2",
            "subband": 317
          }
        },
        {
          "name": "ais002-5",
          "address": "10.144.6.15:45005",
          "input": "10.195.100.30:4005",
          "argv": {
            "affinity": "2,5,7,2",
            "subband": 318
          }
        },
        {
          "name": "ais002-6",
          "address": "10.144.6.15:45006",
          "input": "10.195.100.30:4006",
          "argv": {
            "affinity": "2,9,11,2",
            "subband": 319
          }
        },
        {
          "name": "ais002-7",
          "address": "10.144.6.15:45007",
          "input": "10.195.100.30:4007",
          "argv": {
            "affinity": "2,13,15,2",
            "subband": 320
          }
        },
        {
          "name": "ais003-0",
          "address": "10.144.6.16:45000",
          "input": "10.195.100.40:4000",
          "argv": {
            "affinity": "2,4,6,2",
            "subband": 295
          }
        },
        {
          "name": "ais003-1",
          "address": "10.144.6.16:45001",
          "input": "10.195.100.40:4001",
          "argv": {
            "affinity": "2,8,10,2",
            "subband": 296
          }
        },
        {
          "name": "ais003-2",
          "address": "10.144.6.16:45002",
          "input": "10.195.100.40:4002",
          "argv": {
            "affinity": "2,12,14,2",
            "subband": 297
          }
        },
        {
          "name": "ais003-3",
          "address": "10.144.6.16:45003",
          "input": "10.195.100.40:4003",
          "argv": {
            "affinity": "2,18,20,22,24,26,28,30,2",
            "subband": 298
          }
        },
        {
          "name": "ais003-4",
          "address": "10.144.6.16:45004",
          "input": "10.195.100.40:4004",
          "argv": {
            "affinity": "2,1,3,2",
            "subband": 299
          }
        },
        {
          "name": "ais003-5",
          "address": "10.144.6.16:45005",
          "input": "10.195.100.40:4005",
          "argv": {
            "affinity": "2,5,7,2",
            "subband": 300
          }
        },
        {
          "name": "ais003-6",
          "address": "10.144.6.16:45006",
          "input": "10.195.100.40:4006",
          "argv": {
            "affinity": "2,9,11,2",
            "subband": 301
          }
        },
        {
          "name": "ais003-7",
          "address": "10.144.6.16:45007",
          "input": "10.195.100.40:4007",
          "argv": {
            "affinity": "2,13,15,2",
            "subband": 302
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
            "output" : "dir:/data,srv:9000",
            "subbands" : "313,314,315,316,317,318,319,320,295,296,297,298,299,300,301,302"
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
