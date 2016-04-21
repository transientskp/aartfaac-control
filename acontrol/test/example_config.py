import unittest
import textwrap
import tempfile

EXAMPLE_CONFIG = """
{
  "starttime": "2016-03-07 04:12:47",
  "lba": {
    "modes": ["lba_inner", "lba_outer"],
    "subbands": [
      295,
      296,
      297,
      298,
      299,
      300,
      301,
      302
    ],
    "channels": [
      0,
      62
    ],
    "flagged": [
      2,
      4,
      128
    ]
  },
  "hba": {
    
  },
  "programs": {
    "atv": {
      "address": "10.144.6.13:45000",
      "subband": 299,
      "args": {
        "output": "\/data\/atv",
        "snapshot": "\/var\/www",
        "port": 5000
      }
    },
    "correlator": {
      "address": "10.144.6.31:45000",
      "args": {
        "b": 16
      }
    },
    "server": {
      "address": "10.195.100.30:45000",
      "args": {
        "input-host": "10.195.100.3"
      }
    },
    "pipeline": {
      "address": [
        "10.144.6.19:45000"
      ],
      "args": {
        "ant-sigma": 4,
        "vis-sigma": 3
      }
    }
  }
}
"""
EXAMPLE_CONFIG = textwrap.dedent(EXAMPLE_CONFIG).strip()

LOCAL_CONFIG = """
{
  "starttime": "2016-03-07 04:12:47",
  "lba": {
    "modes": ["lba_inner", "lba_outer"],
    "subbands": [
      295,
      296,
      297,
      298,
      299,
      300,
      301,
      302
    ],
    "channels": [
      0,
      62
    ],
    "flagged": [
      2,
      4,
      128
    ]
  },
  "hba": {
    
  },
  "programs": {
    "atv": {
      "address": "127.0.0.1:45000",
      "subband": 299,
      "args": {
        "output": "\/data\/atv",
        "snapshot": "\/var\/www",
        "port": 5000
      }
    },
    "correlator": {
      "address": "127.0.0.1:46000",
      "args": {
        "b": 16
      }
    },
    "server": {
      "address": "127.0.0.1:47000",
      "args": {
        "buffer-max-size": 64424509440,
        "input-host": "127.0.0.1"
      }
    },
    "pipeline": {
      "address": [
        "127.0.0.1:48000",
        "127.0.0.1:48001"
      ],
      "args": {
        "ant-sigma": 4,
        "vis-sigma": 3
      }
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
