"""Force the offline rule agent so tests are hermetic and network-free."""

import os


os.environ["REPORTFLOW_AGENT"] = "rule"
