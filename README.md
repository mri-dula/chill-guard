# chill-guard 🌡️

> Never freeze (or roast) again. A Raspberry Pi Pico + DHT22 temperature monitor that automatically calls the janitor when your room gets out of range.

## Motivation

Office too cold in winter, too hot in summer — and no one notices until someone complains. Chill Guard sits quietly in the corner, watches the temperature, and calls the janitor the moment something is off. No app, no dashboard, no manual checks.

## How it works

```
DHT22 sensor → Raspberry Pi Pico → USB → Mac (listener.py) → Webhook → Janitor gets called
```

The Pico reads temperature every 30 seconds and streams it over USB. A Python script on the Mac watches that stream and fires a webhook whenever the temperature goes out of range. A 15-minute cooldown prevents repeat calls.

## Hardware

| Component | Notes |
|-----------|-------|
| Raspberry Pi Pico | Standard Pico (not Pico W) |
| DHT22 module | 3-pin breakout — no resistor needed |
| Micro USB cable | Must be a data cable, not charge-only |
| Jumper wires | Female-to-female |

### Wiring

Connect DHT22 to the Pico's **right row of pins** (USB port facing up):

| DHT22 | Pico pin | Position (right row, top to bottom) |
|-------|----------|--------------------------------------|
| `+`   | 3V3      | 5th |
| `out` | GP28     | 7th |
| `-`   | AGND     | 8th |

## Setup

### 1. Flash MicroPython onto the Pico

1. Hold BOOTSEL, plug Pico into Mac via USB, release
2. Open [Thonny](https://thonny.org) → Tools → Options → Interpreter → MicroPython (Raspberry Pi Pico)
3. Click "Install or update MicroPython" → Install

### 2. Upload Pico files

In Thonny, open each file and save to the Pico (File → Save As → Raspberry Pi Pico):
- `main.py`
- `config.py`

Close Thonny, unplug and replug the Pico.

### 3. Configure the listener

```bash
cp listener_config.sample.yaml listener_config.yaml
```

Edit `listener_config.yaml`:
- Set `thresholds.temp_low` and `thresholds.temp_high` (°C)
- Set `webhook.url` to your webhook endpoint
- Adjust `webhook.cooldown` (seconds between calls, default 15 min)

### 4. Run the listener

```bash
uv venv
uv pip install pyserial pyyaml requests
.venv/bin/python listener.py
```

Keep this running on your Mac while the Pico is plugged in. Go to **System Settings → Battery** and disable automatic sleep so it keeps running overnight.

## Configuration reference

```yaml
thresholds:
  temp_low:  18.0   # alert if below this (°C)
  temp_high: 26.0   # alert if above this (°C)

webhook:
  cooldown: 900     # seconds between alerts (900 = 15 min)
  url: "https://..."
  method: POST
  payload:
    action: "{action}"           # "increase" or "decrease"
    current_temperature: "{temperature}"
    level: "{level}"             # "too low" or "too high"
```

## Upgrading to standalone

The current setup requires a Mac to be on and running. To make it fully standalone, swap in a **Raspberry Pi Pico W** (~$6) — it has built-in WiFi and can call the webhook directly, no Mac needed.
