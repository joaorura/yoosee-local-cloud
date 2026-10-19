import asyncio
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger("yoosee_local.udp_sink")


class UdpSinkProtocol(asyncio.DatagramProtocol):
    """Protocol to absorb UDP datagrams without ICMP port unreachable storms."""

    def __init__(self, port_name: str = "udp_sink", reply_ack: bool = False):
        self.port_name = port_name
        self.reply_ack = reply_ack
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.packet_count = 0
        self.bytes_received = 0

    def connection_made(self, transport: asyncio.BaseTransport):
        self.transport = transport  # type: ignore

    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        self.packet_count += 1
        self.bytes_received += len(data)
        logger.debug(
            "[%s] Received %d bytes from %s:%d: %s",
            self.port_name,
            len(data),
            addr[0],
            addr[1],
            data[:32],
        )

        # Optional generic ACK response if the camera handshake needs confirmation
        if self.reply_ack and self.transport:
            # Echo first 8 bytes if header, or send simple 4-byte ACK
            ack_payload = data[:8] if len(data) >= 8 else b"\x00\x00\x00\x00"
            self.transport.sendto(ack_payload, addr)

    def error_received(self, exc: Exception):
        logger.warning("[%s] UDP Error received: %s", self.port_name, exc)


async def start_udp_sinks(
    ports: List[int], host: str = "0.0.0.0", reply_ack: bool = False
) -> Tuple[List[asyncio.DatagramTransport], List[UdpSinkProtocol]]:
    """Bind and start multiple UDP datagram listeners."""
    loop = asyncio.get_running_loop()
    transports = []
    protocols = []

    for port in ports:
        protocol_instance = UdpSinkProtocol(port_name=f"port_{port}", reply_ack=reply_ack)
        transport, _ = await loop.create_datagram_endpoint(
            lambda p=protocol_instance: p,
            local_addr=(host, port),
        )
        transports.append(transport)
        protocols.append(protocol_instance)
        logger.info("UDP Sink listening on %s:%d", host, port)

    return transports, protocols
