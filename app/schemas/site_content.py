# app/schemas/site_content.py
from pydantic import BaseModel
from typing import Dict


class SiteContentBulkUpdate(BaseModel):
    """Admin sends a partial dict of {key: value} to upsert."""
    values: Dict[str, str]


class SiteContentOut(BaseModel):
    """Public GET returns the whole thing flattened into one dict."""
    values: Dict[str, str]