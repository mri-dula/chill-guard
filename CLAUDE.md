# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This project has two distinct runtime environments that must be kept separate:

**Pico (MicroPython)** — runs on the Raspberry Pi Pico hardware:
- `main.py` — reads DHT22 every 30s, prints `34.7°C` lines over USB serial
- `config.py` — hardware config only (`DATA_PIN`, `CHECK_INTERVAL`)

**Mac (Python 3)** — runs on the host machine:
- `listener.py` — reads serial output from the Pico, checks temperature against thresholds, calls the webhook
- `listener_config.yaml` — all runtime config: serial port, thresholds, webhook URL/method/headers/payload

The split is intentional: thresholds and webhook config live on the Mac so they can be changed without re-uploading code to the Pico.

## Running the listener

```bash
uv venv && uv pip install pyserial pyyaml requests   # first time only
cp listener_config.sample.yaml listener_config.yaml  # then fill in your webhook URL
.venv/bin/python listener.py
```

`listener_config.yaml` is gitignored — never commit it. Use `listener_config.sample.yaml` for sharing config structure.

## Deploying to the Pico

Pico files (`main.py`, `config.py`) must be uploaded via **Thonny** (thonny.org):
1. Open Thonny, connect to MicroPython (Raspberry Pi Pico) interpreter
2. Open the file → File → Save As → Raspberry Pi Pico
3. Close Thonny, unplug and replug the Pico

Thonny and `listener.py` cannot run at the same time — they both hold the serial port.

## Webhook payload templating

`listener_config.yaml` payload values support `{action}`, `{temperature}`, and `{level}` placeholders. `REASON_MAP` in `listener.py` maps `too_cold` → `increase`/`too low` and `too_hot` → `decrease`/`too high`.

## notify.py

Currently unused — kept as a stub for future Pico-side notification logic (e.g. if migrating to a Pico W where the Pico calls the webhook directly over WiFi).
