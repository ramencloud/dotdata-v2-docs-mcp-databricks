"""Databricks App entry point for the dotdata-docs MCP server (streamable-http)."""

import os

from starlette.middleware.cors import CORSMiddleware

from dotdata_docs_mcp.server import mcp

_databricks_host = os.environ.get("DATABRICKS_HOST", "").strip().rstrip("/")
_allowed_origins = (
    [_databricks_host if _databricks_host.startswith("https://") else f"https://{_databricks_host}"]
    if _databricks_host
    else [o.strip() for o in os.environ.get("MCP_ALLOWED_ORIGINS", "").split(",") if o.strip()]
)

app = mcp.streamable_http_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins or ["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
