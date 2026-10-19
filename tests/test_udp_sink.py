import asyncio

import pytest

from yoosee_local.udp_sink import UdpSinkProtocol, start_udp_sinks


@pytest.mark.asyncio
async def test_udp_sink_datagram_received():
    loop = asyncio.get_running_loop()

    # Start a test sink on an ephemeral port
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UdpSinkProtocol(port_name="test_32100"),
        local_addr=("127.0.0.1", 0),
    )
    port = transport.get_extra_info("sockname")[1]

    try:
        # Create a client socket and send a sample keepalive packet
        client_transport, client_protocol = await loop.create_datagram_endpoint(
            asyncio.DatagramProtocol,
            remote_addr=("127.0.0.1", port),
        )
        client_transport.sendto(b"p2pu_v2_start_process_keepalive\x00\x01\x02")
        await asyncio.sleep(0.05)

        assert protocol.packet_count == 1
        assert protocol.bytes_received == len(b"p2pu_v2_start_process_keepalive\x00\x01\x02")
        client_transport.close()
    finally:
        transport.close()


@pytest.mark.asyncio
async def test_start_udp_sinks_multiple_ports():
    # Test starting multiple ephemeral sinks
    transports, protocols = await start_udp_sinks(ports=[0, 0], host="127.0.0.1")
    assert len(transports) == 2
    assert len(protocols) == 2

    for t in transports:
        t.close()
