"""Databricks App entry point for the dotdata-v2-docs MCP server (streamable-http)."""

import os

from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.cors import CORSMiddleware

from dotdata_v2_docs_mcp.server import get_mcp

_databricks_host = os.environ.get("DATABRICKS_HOST", "").strip().rstrip("/")
_allowed_origins = (
    [_databricks_host if _databricks_host.startswith("https://") else f"https://{_databricks_host}"]
    if _databricks_host
    else [o.strip() for o in os.environ.get("MCP_ALLOWED_ORIGINS", "").split(",") if o.strip()]
)
_port = os.environ.get("PORT", "8000")
_on_databricks = bool(_databricks_host)  # DATABRICKS_HOST is set by Databricks Apps

# Same settings the FF 1.5 server used on Databricks.
_transport_security = TransportSecuritySettings(
    # Genie calls from the workspace URL; without this the mcp library answers 403 "Invalid Origin header".
    allowed_origins=_allowed_origins,
    # Host header as seen behind the Databricks Apps proxy.
    allowed_hosts=[f"localhost:{_port}", f"127.0.0.1:{_port}", "localhost", "127.0.0.1"],
)

mcp = get_mcp()
app = mcp.streamable_http_app(
    json_response=True,  # plain JSON replies instead of SSE streams
    stateless_http=_on_databricks,  # Genie does not keep Mcp-Session-Id; without this it gets 400 "Missing session ID"
    transport_security=_transport_security,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins or ["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
