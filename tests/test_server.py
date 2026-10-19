import asyncio

import pytest

from yoosee_local.server import ServerConfig, run_server


@pytest.mark.asyncio
async def test_server_startup_and_shutdown():
    config = ServerConfig(
        host="127.0.0.1",
        http_port=0,  # Ephemeral
        udp_ports=[0],  # Ephemeral
    )

    # Start server in task
    stop_event = asyncio.Event()
    task = asyncio.create_task(run_server(config, stop_event=stop_event))

    await asyncio.sleep(0.1)
    # Stop server
    stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)
    assert task.done()
