import pytest
from aiohttp.test_utils import TestClient, TestServer

from yoosee_local.http_mock import create_http_app


@pytest.fixture
async def client():
    app = create_http_app()
    server = TestServer(app)
    cli = TestClient(server)
    await cli.start_server()
    yield cli
    await cli.close()


async def test_root_health(client):
    resp = await client.get("/")
    assert resp.status == 200
    text = await resp.text()
    assert "OK" in text


async def test_generate_204(client):
    resp = await client.get("/generate_204")
    assert resp.status == 204


async def test_checkcer_endpoint(client):
    resp = await client.get("/checkcer")
    assert resp.status == 200
    data = await resp.json()
    assert data["status"] == 1
    assert data["code"] == 0


async def test_catchall_endpoint(client):
    resp = await client.get("/any/other/firmware/path")
    assert resp.status == 200
    text = await resp.text()
    assert "OK" in text


def test_ssl_context_none():
    from yoosee_local.http_mock import create_self_signed_ssl_context

    assert create_self_signed_ssl_context(None, None) is None
