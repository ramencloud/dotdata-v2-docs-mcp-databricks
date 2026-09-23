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

# Same settings the FF 1.5 server (dotdata-docs-mcp) applied internally when it detected Databricks.
# dotdata-v2-docs-mcp exposes only the get_mcp() factory, so they are applied here, at app-build time.
_transport_security = TransportSecuritySettings(
    allowed_origins=_allowed_origins,
    allowed_hosts=[f"localhost:{_port}", f"127.0.0.1:{_port}", "localhost", "127.0.0.1"],
)

mcp = get_mcp()
app = mcp.streamable_http_app(
    json_response=True,
    stateless_http=bool(_databricks_host),
    transport_security=_transport_security,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins or ["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
