import socket
import sys

DIRECTIONS = {
    "up": "UP",
    "down": "DWON",  # Firmware typo required for Anyka AK3918
    "left": "LEFT",
    "right": "RIGHT",
}


def format_ptz_request(ip: str, ptz_cmd: str) -> str:
    """Format the RTSP SET_PARAMETER request for PTZ motor control."""
    return (
        f"SET_PARAMETER rtsp://{ip}/onvif1 RTSP/1.0\r\n"
        f"Content-type: ptzCmd: {ptz_cmd}\r\n"
        f"CSeq: 1\r\n\r\n"
    )


def move_camera(ip_or_host: str, direction: str, timeout: float = 2.0) -> bool:
    """Send a stateless PTZ command to the camera via RTSP port 554."""
    norm_dir = direction.lower().strip()
    if norm_dir not in DIRECTIONS:
        raise ValueError(f"Invalid direction '{direction}'. Choose from {list(DIRECTIONS.keys())}")

    ptz_cmd = DIRECTIONS[norm_dir]
    req = format_ptz_request(ip_or_host, ptz_cmd)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip_or_host, 554))
        s.sendall(req.encode("ascii"))
        resp = s.recv(1024)
        return b"200 OK" in resp
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def main():
    if len(sys.argv) < 3:
        print("Usage: yoosee-ptz <camera_ip> <up|down|left|right>")
        sys.exit(1)

    ip = sys.argv[1]
    direction = sys.argv[2]
    success = move_camera(ip, direction)
    if success:
        print(f"Successfully moved {ip} {direction}")
        sys.exit(0)
    else:
        print(f"Failed to move {ip} {direction}")
        sys.exit(1)


if __name__ == "__main__":
    main()
