# gx_mcp_server/logging.py
import logging
import warnings

# Suppress Great Expectations Marshmallow warnings
warnings.filterwarnings(
    "ignore",
    message=".*Number.*field should not be instantiated.*",
    category=UserWarning
)
try:
    marshmallow_warnings = __import__(
        "marshmallow.warnings", fromlist=["ChangedInMarshmallow4Warning"]
    )
    marshmallow_warning = getattr(
        marshmallow_warnings, "ChangedInMarshmallow4Warning", UserWarning
    )
except Exception:  # pragma: no cover - optional dependency may be absent
    marshmallow_warning = UserWarning

warnings.filterwarnings(
    "ignore",
    category=marshmallow_warning,
)

# Configure logger
logger = logging.getLogger("gx_mcp_server")

# Avoid adding multiple handlers when the module is imported repeatedly
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)