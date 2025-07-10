# gx_mcp_server/logging.py
import logging

# Configure logger
logger = logging.getLogger("gx_mcp_server")

# Avoid adding multiple handlers when the module is imported repeatedly
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)