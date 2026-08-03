"""Test configuration.

Force the offline template answerer for the whole suite so tests are hermetic:
they must not depend on ambient ``OPENAI_API_KEY`` values or network access.
"""

import os


os.environ["EVIDENCEQA_ANSWER_PROVIDER"] = "template"
