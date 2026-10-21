from unittest.mock import MagicMock, patch
import pytest

from yoosee_local.client import YooseeClient


def test_client_ptz_move():
    client = YooseeClient("192.168.2.204")
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.recv.return_value = b"RTSP/1.0 200 OK\r\nCSeq: 1\r\n\r\n"

        assert client.move("up") is True
        mock_sock.connect.assert_called_once_with(("192.168.2.204", 554))
        sent = mock_sock.sendall.call_args[0][0].decode()
        assert "Content-type: ptzCmd: UP" in sent


def test_client_ptz_invalid_dir():
    client = YooseeClient("192.168.2.204")
    with pytest.raises(ValueError):
        client.move("invalid")


def test_client_white_light():
    client = YooseeClient("192.168.2.204")
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.recv.return_value = b"RTSP/1.0 200 OK\r\nCSeq: 1\r\n\r\n"

        assert client.set_white_light(True) is True
        sent = mock_sock.sendall.call_args[0][0].decode()
        assert "Content-type: whiteLight: 1" in sent

        assert client.set_white_light(False) is True
        sent = mock_sock.sendall.call_args[0][0].decode()
        assert "Content-type: whiteLight: 0" in sent


def test_client_auto_tracking():
    client = YooseeClient("192.168.2.204")
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.recv.return_value = b"RTSP/1.0 200 OK\r\nCSeq: 1\r\n\r\n"

        assert client.set_auto_tracking(True) is True
        sent = mock_sock.sendall.call_args[0][0].decode()
        assert "Content-type: autoTrack: 1" in sent


def test_client_sound_and_siren():
    client = YooseeClient("192.168.2.204")
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.recv.return_value = b"RTSP/1.0 200 OK\r\nCSeq: 1\r\n\r\n"

        assert client.play_sound("alarm") is True
        assert client.stop_sound() is True


def test_client_test_connection():
    client = YooseeClient("192.168.2.204")
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        assert client.test_connection() is True

        mock_sock.connect.side_effect = OSError("refused")
        assert client.test_connection() is False
