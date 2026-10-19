# Yoosee Local Cloud

[![CI](https://github.com/joaorura/yoosee-local-cloud/actions/workflows/ci.yml/badge.svg)](https://github.com/joaorura/yoosee-local-cloud/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Yoosee Local Cloud** is a lightweight, zero-dependency local cloud mock, ultra-fast stateless RTSP PTZ controller, and isolated IoT bridge for **Yoosee / Gwelltimes IP cameras** (powered by Anyka AK3918 family SoCs).

It enables **100% offline, cloud-independent, and private** operation inside isolated IoT VLANs while preserving full Pan-Tilt-Zoom (PTZ) capability and seamless integration with **Home Assistant** and **go2rtc**.

---

## Table of Contents

- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Architecture](#architecture)
- [Features](#features)
- [Stateless RTSP PTZ Motor Control](#stateless-rtsp-ptz-motor-control)
- [Fake Cloud Mock & UDP Sink](#fake-cloud-mock--udp-sink)
- [Quickstart](#quickstart)
  - [Installation](#installation)
  - [CLI: yoosee-ptz](#cli-yoosee-ptz)
  - [CLI: yoosee-fake-cloud](#cli-yoosee-fake-cloud)
- [Systemd Daemon Setup](#systemd-daemon-setup)
- [Network & DNS Configuration](#network--dns-configuration)
- [go2rtc Integration](#go2rtc-integration)
- [Home Assistant Integration](#home-assistant-integration)
  - [1. Helper Script](#1-helper-script)
  - [2. YAML Configuration](#2-yaml-configuration)
  - [3. Lovelace Dashboard Card](#3-lovelace-dashboard-card)
- [Tested Hardware & Firmware](#tested-hardware--firmware)
- [Protocol Reverse Engineering](#protocol-reverse-engineering)
- [Development & Testing](#development--testing)
- [Contributing & License](#contributing--license)

---

## The Problem

Yoosee / Gwelltimes IP cameras (widely sold under generic brands and Anyka AK3918 SoCs) are inexpensive and feature decent optical hardware, but their firmware is strictly tied to Chinese cloud services:

1. **WAN Dependency & Watchdogs:** When blocked from accessing the internet via firewall or VLAN isolation, camera daemons flood the network with DNS lookups and UDP heartbeats. Many firmware revisions will eventually crash, drop RTSP video streams, or enter reboot loops when cloud servers do not acknowledge heartbeats.
2. **Cloud-Locked PTZ:** Motor controls (Pan-Tilt-Zoom) are conventionally gated behind the proprietary Yoosee mobile app via cloud P2P signaling, while ONVIF PTZ profile support is broken or unauthenticated.
3. **Privacy Concerns:** Without complete isolation, cameras continuously transmit telemetry, network metadata, and P2P connection requests to foreign servers.

---

## The Solution

By disassembling the camera binary (`/ipc/ipc`) and official Gwelltimes SDK libraries, we discovered:

- **Unauthenticated Native RTSP PTZ:** The camera firmware listens on standard RTSP port 554 and responds to stateless `SET_PARAMETER` requests with a sub-20ms latency.
- **Heartbeat & Connectivity Keepalive:** Camera watchdogs only require simple HTTP `200 OK` connectivity checks and generic UDP acknowledgment packets on their signaling ports.

This repository provides:
- **`yoosee-fake-cloud`**: A lightweight asynchronous server that satisfies HTTP/HTTPS connectivity checks and sinks multi-port UDP keepalives.
- **`yoosee-ptz`**: A CLI and Python library to dispatch immediate PTZ movements without stream disruption.
- **Home Assistant & go2rtc Blueprints**: Ready-to-use configuration files and Lovelace cards for zero-latency WebRTC live views and D-Pad controls.

---

## Architecture

```
                       +---------------------------------------+
                       |           Isolated IoT VLAN           |
                       +---------------------------------------+
                                          |
          +-------------------------------+-------------------------------+
          | (192.168.2.204)               | (192.168.2.201)               | (192.168.2.185)
   [ Yoosee Camera: Entrada ]      [ Yoosee Camera: Lavanderia ]   [ Yoosee Camera: Gourmet ]
          |          |                    |          |                    |          |
          | RTSP 554 | DNS Spoofed        | RTSP 554 | DNS Spoofed        | RTSP 554 | DNS Spoofed
          | (Video)  | (Cloud HTTP/UDP)   | (Video)  | (Cloud HTTP/UDP)   | (Video)  | (Cloud HTTP/UDP)
          |          |                    |          |                    |          |
          v          v                    v          v                    v          v
   +---------------+ +------------------+ |          |                    |          |
   |    go2rtc     | | yoosee-fake-cloud|<+----------+--------------------+----------+
   | (WebRTC / H264| |  (HTTP 80 / UDP  |
   |  Restreaming) | | 32100, 18443...) |
   +-------+-------+ +------------------+
           |
           | WebRTC Stream
           v
   +-------------------------------------------------------------+
   |                       Home Assistant                        |
   |                                                             |
   |  [Lovelace WebRTC Card] ---> [D-Pad Directional Buttons]    |
   |                                           |                 |
   |                                           v                 |
   |                              [shell_command.yoosee_ptz]     |
   |                                           |                 |
   |                              (RTSP SET_PARAMETER :554)      |
   +-------------------------------------------+-----------------+
                                               |
                                               v (sub-20ms)
                                    [ Camera Moves Instantly ]
```

---

## Features

- **Blazing Fast PTZ (~20 ms response):** Direct socket connection via RTSP `SET_PARAMETER`. No session initialization (`SETUP`/`PLAY`) needed.
- **Firmware Typo Compatibility:** Automatically handles the Anyka firmware bug where downward movement is hardcoded as `DWON`.
- **Zero Cloud Leakage:** Satisfies camera watchdogs locally, allowing complete blocking of WAN access at the firewall level.
- **Multi-Port UDP Keepalive Sink:** Binds to standard Yoosee signaling ports (`32100`, `32108`, `18443`, `18800`, `19800`) with optional ACK replies.
- **On-Demand Streaming:** Fully compatible with `go2rtc` for instant RTSP/WebRTC viewing with negligible idle CPU and memory consumption.
- **Home Assistant Ready:** Includes template buttons, shell commands, and Lovelace cards for immediate integration.

---

## Stateless RTSP PTZ Motor Control

Anyka AK3918 firmware exposes an unauthenticated, stateless control interface over RTSP:

```http
SET_PARAMETER rtsp://<CAMERA_IP>/onvif1 RTSP/1.0
Content-type: ptzCmd: <COMMAND>
CSeq: 1

```

### Commands

| Direction | Command | Internal Firmware Routine | Notes |
|---|---|---|---|
| **Up** | `UP` | `vAddKey(0x0c)` | Moves camera up one step |
| **Down** | `DWON` | `vAddKey(0x0d)` | **Firmware Typo:** Hardcoded as `DWON` in `/ipc/ipc` at offset `0x340308` |
| **Left** | `LEFT` | `vAddKey(0x0e)` | Moves camera left one step |
| **Right** | `RIGHT` | `vAddKey(0x0f)` | Moves camera right one step |

### Response
```http
RTSP/1.0 200 OK
CSeq: 1
Session: 
Content-Length: 0
```

`yoosee-ptz` abstracts this protocol completely: passing `"down"` automatically sends `"DWON"` to the camera.

---

## Fake Cloud Mock & UDP Sink

When cameras boot or operate, they contact cloud endpoints via HTTP and UDP:
- **HTTP/HTTPS Checks:** GET/POST requests verifying internet routing and time synchronization. `yoosee-fake-cloud` returns instant `200 OK` JSON responses.
- **UDP Heartbeats:** Cameras send periodic keepalives to ports `32100`, `32108`, `18443`, `18800`, `19800`. `yoosee-fake-cloud` consumes these packets and replies with an ACK frame when `--reply-ack` is enabled.

---

## Quickstart

### Installation

```bash
# Clone the repository
git clone https://github.com/joaorura/yoosee-local-cloud.git
cd yoosee-local-cloud

# Install using pip
pip install .

# For development:
pip install -e ".[dev]"
```

### CLI: yoosee-ptz

Move any camera immediately from the terminal:

```bash
# Move camera up
yoosee-ptz 192.168.2.204 up

# Move camera down (handles DWON automatically)
yoosee-ptz 192.168.2.204 down

# Move camera left
yoosee-ptz 192.168.2.204 left

# Move camera right
yoosee-ptz 192.168.2.204 right
```

Python library usage:
```python
from yoosee_local.ptz import move_camera

success = move_camera("192.168.2.204", "up")
if success:
    print("Camera moved!")
```

### CLI: yoosee-fake-cloud

Start the mock cloud and UDP keepalive sink:

```bash
# Run with default settings (HTTP port 8080, UDP ports 32100, 32108, 18443, 18800, 19800)
yoosee-fake-cloud --reply-ack

# Run on privileged HTTP port 80:
sudo yoosee-fake-cloud --host 0.0.0.0 --http-port 80 --reply-ack -v
```

---

## Systemd Daemon Setup

For persistent background operation on a Linux server or Home Assistant host:

1. Copy the systemd unit file:
   ```bash
   sudo cp systemd/yoosee-fake-cloud.service /etc/systemd/system/
   ```

2. Adjust the binary path in `/etc/systemd/system/yoosee-fake-cloud.service` if installed in a virtualenv.

3. Reload and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now yoosee-fake-cloud
   ```

4. Inspect logs:
   ```bash
   journalctl -u yoosee-fake-cloud -f
   ```

---

## Network & DNS Configuration

To redirect camera cloud traffic to your local mock server:

1. **Firewall / VLAN Rule:** Block all WAN outbound traffic for the camera IPs/VLAN.
2. **Local DNS Rewrite (Pi-hole / AdGuard Home / dnsmasq / router):**
   Redirect the following domains to the IP running `yoosee-fake-cloud`:
   ```text
   *.gw.bshare.com.cn
   *.cloud.yoosee.co
   *.gwelltimes.com
   cloud.cloudlinks.cn
   ```

Example `dnsmasq` rule:
```conf
address=/gw.bshare.com.cn/192.168.2.10
address=/cloud.yoosee.co/192.168.2.10
address=/gwelltimes.com/192.168.2.10
address=/cloudlinks.cn/192.168.2.10
```

---

## go2rtc Integration

Yoosee cameras stream H.264 video on `rtsp://<camera_ip>:554/onvif1`. Using [go2rtc](https://github.com/AlexxIT/go2rtc) allows zero-latency WebRTC streaming in Home Assistant with on-demand RTSP connections (saving camera CPU and bandwidth).

Add to your `go2rtc.yaml`:

```yaml
streams:
  camera_entrada:
    - rtsp://admin:123456@192.168.2.204:554/onvif1#backchannel=0
  camera_lavanderia:
    - rtsp://admin:123456@192.168.2.201:554/onvif1#backchannel=0
  camera_gourmet:
    - rtsp://admin:123456@192.168.2.185:554/onvif1#backchannel=0

webrtc:
  listen: ":8555"
```

---

## Home Assistant Integration

### 1. Helper Script

Copy `homeassistant/scripts/yoosee_ptz.py` into your Home Assistant `/config/scripts/` directory:

```bash
mkdir -p /config/scripts
cp homeassistant/scripts/yoosee_ptz.py /config/scripts/
chmod +x /config/scripts/yoosee_ptz.py
```

### 2. YAML Configuration

Add the contents of [`homeassistant/configuration_example.yaml`](homeassistant/configuration_example.yaml) to your `configuration.yaml`:

```yaml
shell_command:
  yoosee_ptz: "python3 /config/scripts/yoosee_ptz.py {{ camera }} {{ direction }}"

template:
  - button:
      - name: "Entrada Mover Cima"
        unique_id: camera_entrada_mover_cima
        icon: "mdi:arrow-up-bold"
        press:
          action: shell_command.yoosee_ptz
          data:
            camera: "entrada"
            direction: "up"

      - name: "Entrada Mover Baixo"
        unique_id: camera_entrada_mover_baixo
        icon: "mdi:arrow-down-bold"
        press:
          action: shell_command.yoosee_ptz
          data:
            camera: "entrada"
            direction: "down"

      - name: "Entrada Mover Esquerda"
        unique_id: camera_entrada_mover_esquerda
        icon: "mdi:arrow-left-bold"
        press:
          action: shell_command.yoosee_ptz
          data:
            camera: "entrada"
            direction: "left"

      - name: "Entrada Mover Direita"
        unique_id: camera_entrada_mover_direita
        icon: "mdi:arrow-right-bold"
        press:
          action: shell_command.yoosee_ptz
          data:
            camera: "entrada"
            direction: "right"
```

### 3. Lovelace Dashboard Card

Use the example card from [`homeassistant/lovelace_card_example.yaml`](homeassistant/lovelace_card_example.yaml) combining `custom:webrtc-camera` with a 3x3 D-Pad grid:

```yaml
type: vertical-stack
title: Câmera Entrada (Yoosee PTZ)
cards:
  - type: custom:webrtc-camera
    entity: camera.camera_entrada

  - type: grid
    columns: 3
    square: true
    cards:
      - type: custom:button-card
        color_type: blank-card
      - type: button
        icon: mdi:arrow-up-bold
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.entrada_mover_cima
      - type: custom:button-card
        color_type: blank-card

      - type: button
        icon: mdi:arrow-left-bold
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.entrada_mover_esquerda
      - type: button
        icon: mdi:crosshairs-gps
        tap_action:
          action: none
      - type: button
        icon: mdi:arrow-right-bold
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.entrada_mover_direita

      - type: custom:button-card
        color_type: blank-card
      - type: button
        icon: mdi:arrow-down-bold
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: button.entrada_mover_baixo
      - type: custom:button-card
        color_type: blank-card
```

---

## Tested Hardware & Firmware

| Device / Model | Chipset (SoC) | Firmware Version | RTSP PTZ | Cloud Mock |
|---|---|---|:---:|:---:|
| Generic Yoosee PTZ Dome | Anyka AK3918EV200 | 46.0.0.53 | :white_check_mark: | :white_check_mark: |
| Outdoor Dual-Lens PTZ | Anyka AK3918EV300 | 46.0.53 | :white_check_mark: | :white_check_mark: |
| Indoor Cube Camera | Anyka AK3918AV100 | 45.x.x.x | :white_check_mark: | :white_check_mark: |

---

## Protocol Reverse Engineering

Detailed technical notes from reverse engineering the firmware `/ipc/ipc` binary, Gwelltimes Android SDKs (`GWP2PSDK`), and SD card `.av` file format are documented in:

:book: [**docs/protocol-reverse-engineering.md**](docs/protocol-reverse-engineering.md)

Key findings include:
- Unauthenticated RTSP `SET_PARAMETER` method and firmware opcode mapping.
- Hardcoded DES keys (`53a6c99d783a68b1`) and TEA keys (`UK*@3oKpFlVVnads`) in Gwelltimes libraries.
- SD Card FAT32/exFAT structure (`/mnt/disc1/npc/record/`) and lossless `ffmpeg` conversion from `.av` to `.mp4`.

---

## Development & Testing

This project adheres to **Test-Driven Development (TDD)** and strict linting.

```bash
# Run test suite with pytest & coverage
PYTHONPATH=src pytest -v

# Run linter
ruff check .

# Check code formatting
black --check .
```

---

## Contributing & License

Contributions are very welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more details.
