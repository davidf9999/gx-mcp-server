# gx_mcp_server/core/schema.py
from typing import Any, Dict

from pydantic import BaseModel


class DatasetHandle(BaseModel):
    handle: str


class SuiteHandle(BaseModel):
    suite_name: str


class ToolResponse(BaseModel):
    success: bool
    message: str


class ValidationResult(BaseModel):
    validation_id: str


class ValidationResultDetail(BaseModel):
    statistics: Dict[str, Any]
    results: Any
    success: bool
