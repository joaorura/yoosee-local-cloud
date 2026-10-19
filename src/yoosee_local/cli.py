import argparse
import asyncio
import logging
import signal

from yoosee_local.server import ServerConfig, run_server


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Yoosee Local Cloud - Mock cloud, PTZ and watchdog sink for Yoosee IP cameras"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Binding host interface (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=8080,
        help="HTTP port for connectivity mock (default: 8080)",
    )
    parser.add_argument(
        "--https-port",
        type=int,
        default=None,
        help="HTTPS port for connectivity mock (default: None)",
    )
    parser.add_argument("--ssl-cert", type=str, default=None, help="Path to TLS certificate file")
    parser.add_argument("--ssl-key", type=str, default=None, help="Path to TLS private key file")
    parser.add_argument(
        "--udp-ports",
        nargs="+",
        type=int,
        default=[32100, 32108, 18443, 18800, 19800],
        help="UDP ports to sink keepalive packets (default: 32100 32108 18443 18800 19800)",
    )
    parser.add_argument(
        "--reply-ack",
        action="store_true",
        help="Reply with generic ACK to UDP keepalives",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    return parser.parse_args(args)


def main():
    args = parse_args()
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = ServerConfig(
        host=args.host,
        http_port=args.http_port,
        https_port=args.https_port,
        ssl_cert=args.ssl_cert,
        ssl_key=args.ssl_key,
        udp_ports=args.udp_ports,
        reply_udp_ack=args.reply_ack,
    )

    stop_event = asyncio.Event()

    def _handle_signal(*_):
        stop_event.set()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_signal)
        except NotImplementedError:
            pass  # Windows fallback

    try:
        loop.run_until_complete(run_server(config, stop_event=stop_event))
    finally:
        loop.close()


if __name__ == "__main__":
    main()
