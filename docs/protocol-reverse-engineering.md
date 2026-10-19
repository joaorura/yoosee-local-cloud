# Yoosee / Gwelltimes Reverse Engineering & Protocol Reference

This document compiles technical findings from disassembling the Anyka AK3918 firmware binary (`/ipc/ipc`) and official Gwelltimes SDKs (`GWP2PSDK`, `p2p-core-release.aar`, `DeviceUDPLib`).

---

## 1. Local RTSP Motor Control (Port 554)

Despite the official mobile app relying on cloud P2P signaling to move cameras, the Anyka AK3918 firmware (`46.0.53` and older) exposes an unauthenticated, stateless PTZ interface via standard RTSP `SET_PARAMETER`:

```http
SET_PARAMETER rtsp://<CAMERA_IP>/onvif1 RTSP/1.0\r\n
Content-type: ptzCmd: <COMMAND>\r\n
CSeq: 1\r\n\r\n
```

### Valid Direction Commands
* `UP` -> Calls internal routine `vAddKey(0x0c)`
* `DWON` -> Calls internal routine `vAddKey(0x0d)` *(Note: The misspelling `DWON` is hardcoded in the firmware binary at offset `0x340308`)*
* `LEFT` -> Calls internal routine `vAddKey(0x0e)`
* `RIGHT` -> Calls internal routine `vAddKey(0x0f)`

### Response
```http
RTSP/1.0 200 OK\r\n
CSeq: 1\r\n
Session: \r\n
Content-Length: 0\r\n\r\n
```
Average response time: **~20 ms**. Does not require allocating an RTP streaming session (`SETUP`/`PLAY`).

---

## 2. SD Card Storage Architecture

Recordings are written to `/mnt/disc1/npc/record/` (or `/mnt/disc0/npc/record/`) formatted with FAT32 or exFAT.

### File Naming Convention
```
%s/%04d-%02d-%02d/%02d.%02d.%02d_%c.av
```
Example: `2026-10-19/14.30.00_A.av`

* `_A.av`: **Alarm** (Motion detection trigger)
* `_M.av`: **Manual** (User recorded)
* `_S.av`: **Schedule** (Continuous recording)

### Format
Files have an `avhead` header (32 bytes) followed by raw multiplexed H.264/H.265 video frames and PCM G.711a audio. It can be converted losslessly using ffmpeg:
```bash
ffmpeg -i 14.30.00_A.av -c copy recording.mp4
```

---

## 3. P2P Transport & Cryptography

* **Default P2P DES Key:** `53a6c99d783a68b1` (hardcoded in `libp2pav.so` for numeric password encryption).
* **TEA Key:** `UK*@3oKpFlVVnads` (used in Tencent Mars Xlog encryption).
* **RTSP Realm:** `HIipCamera` (Password derived via `MD5(device_id)`).
