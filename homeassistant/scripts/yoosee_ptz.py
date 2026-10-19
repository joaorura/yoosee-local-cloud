#!/usr/bin/env python3
"""
Home Assistant Standalone Helper for Yoosee IP Cameras.
Place this script in `/config/scripts/yoosee_ptz.py`.
"""

import socket
import sys

DIRECTIONS = {
    "up": "UP",
    "down": "DWON",
    "left": "LEFT",
    "right": "RIGHT",
}

CAMERAS = {
    "entrada": "192.168.2.204",
    "lavanderia": "192.168.2.201",
    "gourmet": "192.168.2.185",
    "area_gourmet": "192.168.2.185",
}


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 yoosee_ptz.py <ip_or_camera_name> <up|down|left|right>")
        sys.exit(1)

    target = sys.argv[1].lower()
    cam_ip = CAMERAS.get(target, sys.argv[1])
    direction = sys.argv[2].lower()

    if direction not in DIRECTIONS:
        print(f"Invalid direction: {direction}")
        sys.exit(1)

    cmd = DIRECTIONS[direction]
    req = (
        f"SET_PARAMETER rtsp://{cam_ip}/onvif1 RTSP/1.0\r\n"
        f"Content-type: ptzCmd: {cmd}\r\n"
        f"CSeq: 1\r\n\r\n"
    )

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    try:
        s.connect((cam_ip, 554))
        s.sendall(req.encode("ascii"))
        resp = s.recv(1024)
        if b"200 OK" in resp:
            sys.exit(0)
        sys.exit(1)
    except Exception:
        sys.exit(1)
    finally:
        try:
            s.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
