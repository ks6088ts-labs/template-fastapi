from fastapi_mcp import FastApiMCP

from template_fastapi.app import app as fastapi_app

mcp = FastApiMCP(fastapi_app)

mcp.mount()
