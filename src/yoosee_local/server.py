import asyncio
import logging
from dataclasses import dataclass, field
from typing import List, Optional

from aiohttp import web

from yoosee_local.http_mock import create_http_app, create_self_signed_ssl_context
from yoosee_local.udp_sink import start_udp_sinks

logger = logging.getLogger("yoosee_local.server")


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    http_port: int = 8080
    https_port: Optional[int] = None
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    udp_ports: List[int] = field(default_factory=lambda: [32100, 32108, 18443, 18800, 19800])
    reply_udp_ack: bool = False


async def run_server(config: ServerConfig, stop_event: Optional[asyncio.Event] = None):
    """Run both HTTP(S) and multi-port UDP services under one asyncio loop."""
    app = create_http_app()
    runner = web.AppRunner(app)
    await runner.setup()

    # HTTP site
    site = web.TCPSite(runner, config.host, config.http_port)
    await site.start()
    logger.info("HTTP service running on %s:%d", config.host, config.http_port)

    # HTTPS site (if configured)
    ssl_ctx = create_self_signed_ssl_context(config.ssl_cert, config.ssl_key)
    https_site = None
    if ssl_ctx and config.https_port:
        https_site = web.TCPSite(runner, config.host, config.https_port, ssl_context=ssl_ctx)
        await https_site.start()
        logger.info("HTTPS service running on %s:%d", config.host, config.https_port)

    # UDP Sinks
    transports, protocols = await start_udp_sinks(
        ports=config.udp_ports, host=config.host, reply_ack=config.reply_udp_ack
    )

    if stop_event is None:
        stop_event = asyncio.Event()

    try:
        await stop_event.wait()
    finally:
        logger.info("Shutting down services...")
        for t in transports:
            t.close()
        await runner.cleanup()
        logger.info("Shutdown complete.")
