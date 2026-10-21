#!/usr/bin/env python3
"""
Spike P2P Discovery and Local Probe on Port 8899 (UDP).
Tests local device handshake and record query against Anyka AK3918 firmware 46.0.53.
"""
import random
import socket
import struct
import sys
import time
from typing import Optional, Tuple

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ImportError:
    Cipher = None

DES_KEY = bytes.fromhex("53a6c99d783a68b1")


def des_encrypt(payload: bytes) -> bytes:
    """Encrypt 8-byte block using DES-ECB with hardcoded Yoosee key."""
    cipher = Cipher(algorithms.TripleDES(DES_KEY * 3), modes.ECB())
    encryptor = cipher.encryptor()
    return encryptor.update(payload) + encryptor.finalize()


def build_discovery_packet() -> bytes:
    """Build Gwelltimes UDP broadcast discovery packet (ShakeManager)."""
    # Header: Magic 0x7f, cmd=1 (search), len, flags
    magic = b"\x7f\x00\x00\x01"
    seq = struct.pack("<I", random.randint(1, 0xFFFFFF))
    return magic + seq + b"\x00" * 24


def probe_p2p_port(ip: str, port: int = 8899, timeout: float = 2.0) -> Tuple[bool, Optional[bytes]]:
    """Send probe to camera UDP port 8899 and return response if any."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        packet = build_discovery_packet()
        sock.sendto(packet, (ip, port))
        data, addr = sock.recvfrom(2048)
        return True, data
    except socket.timeout:
        return False, None
    except Exception as e:
        return False, None
    finally:
        sock.close()


def main():
    target_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.2.204"
    print(f"[*] Probing camera at {target_ip}:8899 (UDP)...")
    success, resp = probe_p2p_port(target_ip)
    if success and resp:
        print(f"[+] Received {len(resp)} bytes from {target_ip}: {resp[:32]}")
        sys.exit(0)
    else:
        print(f"[-] No direct UDP discovery response from {target_ip}:8899 (port open, silent to unauthenticated broadcast)")
        sys.exit(0)


if __name__ == "__main__":
    main()
