# gx_mcp_server/logging.py
import logging
import os
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
class _OTelFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        record.otel = os.getenv("OTEL_RESOURCE_ATTRIBUTES", "")
        return True


if not logger.handlers:
    handler = logging.StreamHandler()
    handler.addFilter(_OTelFilter())
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s %(otel)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
