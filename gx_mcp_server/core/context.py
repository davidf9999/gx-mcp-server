# gx_mcp_server/core/context.py
"""
Shared Great Expectations context management.

This module provides a singleton Great Expectations context that persists
across all MCP tool calls, ensuring suites and expectations remain available.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from great_expectations.data_context import AbstractDataContext

from gx_mcp_server.logging import logger

import great_expectations as gx

# Global context instance
_context: Optional[AbstractDataContext] = None
_temp_dir: Optional[tempfile.TemporaryDirectory] = None


def get_shared_context() -> AbstractDataContext:
    """
    Get or create a shared Great Expectations context.
    
    This context persists across all MCP tool calls, ensuring that
    suites and expectations remain available throughout the session.
    
    Returns:
        FileDataContext: Shared GX context instance
    """
    global _context, _temp_dir
    
    if _context is None:
        logger.debug("Creating new shared Great Expectations context")
        
        # Create a temporary directory that will be cleaned up automatically
        _temp_dir = tempfile.TemporaryDirectory(prefix="gx_mcp_")
        project_root = Path(_temp_dir.name)
        
        # Initialize a new GX project in the temp directory
        _context = gx.get_context(project_root_dir=project_root)
        
        logger.info("Created persistent GX context at: %s", project_root)
    
    return _context


def reset_context() -> None:
    """Reset the shared context (mainly for testing)."""
    global _context, _temp_dir
    
    # Clear the GX_HOME environment variable
    if "GX_HOME" in os.environ:
        del os.environ["GX_HOME"]
    
    _context = None
    _temp_dir = None
    logger.debug("Reset shared Great Expectations context")