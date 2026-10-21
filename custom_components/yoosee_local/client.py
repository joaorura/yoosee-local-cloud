"""Client for communication with Yoosee / Anyka IP cameras via RTSP."""
import logging
import socket
from typing import Optional

from .const import DEFAULT_PORT, DEFAULT_TIMEOUT, DIRECTIONS

_LOGGER = logging.getLogger(__name__)


class YooseeClient:
    """Client implementing RTSP SET_PARAMETER commands for Yoosee Anyka cameras."""

    def __init__(self, host: str, port: int = DEFAULT_PORT, timeout: float = DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_rtsp_command(self, header: str, value: str) -> bool:
        """Send a stateless RTSP SET_PARAMETER command to the camera."""
        req = (
            f"SET_PARAMETER rtsp://{self.host}/onvif1 RTSP/1.0\r\n"
            f"Content-type: {header}: {value}\r\n"
            f"CSeq: 1\r\n\r\n"
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((self.host, self.port))
            sock.sendall(req.encode("ascii"))
            resp = sock.recv(1024)
            return b"200 OK" in resp
        except Exception as err:
            _LOGGER.debug("RTSP command %s: %s failed on %s: %s", header, value, self.host, err)
            return False
        finally:
            try:
                sock.close()
            except Exception:
                pass

    def move(self, direction: str) -> bool:
        """Send PTZ move command (up, down, left, right)."""
        norm_dir = direction.lower().strip()
        if norm_dir not in DIRECTIONS:
            raise ValueError(f"Invalid direction: {direction}")
        ptz_cmd = DIRECTIONS[norm_dir]
        return self.send_rtsp_command("ptzCmd", ptz_cmd)

    def set_white_light(self, state: bool) -> bool:
        """Toggle white light / spotlight."""
        val = "1" if state else "0"
        return self.send_rtsp_command("whiteLight", val)

    def set_auto_tracking(self, state: bool) -> bool:
        """Toggle auto motion tracking."""
        val = "1" if state else "0"
        return self.send_rtsp_command("autoTrack", val)

    def play_sound(self, sound_name: str) -> bool:
        """Trigger camera sound / siren."""
        # Open audio control and play specified sound
        self.send_rtsp_command("playSound", sound_name)
        return self.send_rtsp_command("AudioCtlCmd", "OPEN")

    def stop_sound(self) -> bool:
        """Stop currently playing sound / siren."""
        return self.send_rtsp_command("AudioCtlCmd", "CLOSE")

    def test_connection(self) -> bool:
        """Test basic TCP reachability to camera RTSP port."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((self.host, self.port))
            return True
        except Exception:
            return False
        finally:
            try:
                sock.close()
            except Exception:
                pass
