# gx_mcp_server/logging.py
import logging
import warnings

# Suppress Great Expectations Marshmallow warnings
warnings.filterwarnings(
    "ignore",
    message=".*Number.*field should not be instantiated.*",
    category=UserWarning
)
warnings.filterwarnings(
    "ignore",
    category=getattr(__import__("marshmallow.warnings", fromlist=["ChangedInMarshmallow4Warning"]), "ChangedInMarshmallow4Warning", UserWarning)
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