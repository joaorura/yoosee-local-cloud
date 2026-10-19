import ssl
from typing import Optional

from aiohttp import web


async def handle_root(request: web.Request) -> web.Response:
    """Respond 200 OK to connectivity checks."""
    return web.Response(text="OK\n", content_type="text/plain")


async def handle_generate_204(request: web.Request) -> web.Response:
    """Respond 204 No Content to Google connectivity probes."""
    return web.Response(status=204)


async def handle_checkcer(request: web.Request) -> web.Response:
    """Respond to Yoosee /checkcer endpoint with valid certificate status."""
    return web.json_response({"status": 1, "code": 0, "message": "valid"})


async def handle_catchall(request: web.Request) -> web.Response:
    """Fallback handler returning 200 OK to absorb arbitrary cloud endpoints."""
    return web.Response(text="OK\n", content_type="text/plain")


def create_http_app() -> web.Application:
    """Create and configure the aiohttp mock application."""
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/generate_204", handle_generate_204)
    app.router.add_get("/checkcer", handle_checkcer)
    app.router.add_get("/{tail:.*}", handle_catchall)
    return app


def create_self_signed_ssl_context(
    cert_path: Optional[str] = None, key_path: Optional[str] = None
) -> Optional[ssl.SSLContext]:
    """Create an SSL context for TLS port 443 termination."""
    if not cert_path or not key_path:
        return None
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.load_cert_chain(cert_path, key_path)
    return ssl_ctx
