import os
import sys
import warnings

# Suppress Great Expectations warnings
try:
    from marshmallow.warnings import ChangedInMarshmallow4Warning
    warnings.filterwarnings("ignore", category=ChangedInMarshmallow4Warning)
except ImportError:
    pass

warnings.filterwarnings(
    "ignore",
    message=".*Number.*field should not be instantiated.*"
)

# Ensure project root is on sys.path for module imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
