from unittest.mock import MagicMock, patch

import pytest

import yoosee_local.ptz
from yoosee_local.ptz import (
    DIRECTIONS,
    format_ptz_request,
    move_camera,
)


def test_directions_mapping():
    assert DIRECTIONS["up"] == "UP"
    assert DIRECTIONS["down"] == "DWON"  # Typo in Anyka firmware must be preserved
    assert DIRECTIONS["left"] == "LEFT"
    assert DIRECTIONS["right"] == "RIGHT"


def test_format_ptz_request():
    req = format_ptz_request("192.168.2.204", "DWON")
    assert "SET_PARAMETER rtsp://192.168.2.204/onvif1 RTSP/1.0\r\n" in req
    assert "Content-type: ptzCmd: DWON\r\n" in req
    assert "CSeq: 1\r\n\r\n" in req


def test_move_camera_success():
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.recv.return_value = b"RTSP/1.0 200 OK\r\nCSeq: 1\r\n\r\n"

        success = move_camera("192.168.2.204", "down", timeout=2.0)
        assert success is True

        mock_sock.connect.assert_called_once_with(("192.168.2.204", 554))
        sent_data = mock_sock.sendall.call_args[0][0].decode()
        assert "Content-type: ptzCmd: DWON" in sent_data
        mock_sock.close.assert_called_once()


def test_move_camera_timeout():
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.connect.side_effect = TimeoutError("Connection timed out")

        success = move_camera("192.168.2.204", "up", timeout=1.0)
        assert success is False
        mock_sock.close.assert_called_once()


def test_move_camera_invalid_direction():
    with pytest.raises(ValueError, match="Invalid direction"):
        move_camera("192.168.2.204", "diagonal")


def test_main_cli_success(monkeypatch, capsys):
    with patch("yoosee_local.ptz.move_camera", return_value=True):
        monkeypatch.setattr("sys.argv", ["yoosee-ptz", "192.168.2.204", "left"])
        with pytest.raises(SystemExit) as exc:
            yoosee_local.ptz.main()
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "Successfully moved" in captured.out


def test_main_cli_missing_args(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["yoosee-ptz"])
    with pytest.raises(SystemExit) as exc:
        yoosee_local.ptz.main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Usage:" in captured.out
