"""
Simple example of using FastAPI-MCP to add an MCP server to a FastAPI app.
ref. https://github.com/tadata-org/fastapi_mcp/blob/v0.3.4/examples/shared/apps/items.py
"""

import uuid
from os import getenv

from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Span

from template_fastapi.routers import agents, chats, demos, files, foodies, items, speeches

app = FastAPI()

# If APPLICATIONINSIGHTS_CONNECTION_STRING exists, configure Azure Monitor
AZURE_CONNECTION_STRING = getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if AZURE_CONNECTION_STRING:

    def server_request_hook(span: Span, scope: dict):
        if span and span.is_recording():
            try:
                # Application Insights に送るデータにユーザ ID を追加する
                user_id = uuid.uuid4().hex  # Replace with actual user ID retrieval logic
                span.set_attribute("enduser.id", user_id)
            except KeyError:
                pass

    configure_azure_monitor(
        connection_string=AZURE_CONNECTION_STRING,
        # enable_live_metrics=True,
        server_request_hook=server_request_hook,
    )
    FastAPIInstrumentor.instrument_app(app)

# Include routers
# Routers configuration list
routersConfig = [
    {
        "router": agents.router,
        "prefix": "/agents",
        "tags": ["agents"],
    },
    {
        "router": chats.router,
        "prefix": "/chats",
        "tags": ["chats"],
    },
    {
        "router": demos.router,
        "prefix": "/demos",
        "tags": ["demos"],
    },
    {
        "router": files.router,
        "prefix": "/files",
        "tags": ["files"],
    },
    {
        "router": foodies.router,
        "prefix": "/foodies",
        "tags": ["foodies"],
    },
    {
        "router": items.router,
        "prefix": "/items",
        "tags": ["items"],
    },
    {
        "router": speeches.router,
        "prefix": "/speeches",
        "tags": ["speeches"],
    },
]

# Include routers using a loop
for routerConfig in routersConfig:
    app.include_router(
        router=routerConfig["router"],
        prefix=routerConfig["prefix"],
        tags=routerConfig["tags"],
        responses={
            404: {
                "description": "Not found",
            },
        },
    )
