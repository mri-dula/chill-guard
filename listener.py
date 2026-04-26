import glob
import time

import requests
import serial
import yaml

REASON_MAP = {
    "too_cold": {"action": "increase", "level": "too low"},
    "too_hot":  {"action": "decrease", "level": "too high"},
}


def load_config():
    with open("listener_config.yaml") as f:
        return yaml.safe_load(f)


def find_pico_port():
    candidates = glob.glob("/dev/cu.usbmodem*")
    if not candidates:
        raise RuntimeError("Pico not found. Make sure it is plugged in.")
    return candidates[0]


def check_thresholds(cfg, temperature):
    temp_low  = cfg["thresholds"]["temp_low"]
    temp_high = cfg["thresholds"]["temp_high"]
    if temperature < temp_low:
        return "too_cold"
    if temperature > temp_high:
        return "too_hot"
    return None


def build_request(cfg, reason, temperature):
    webhook = cfg["webhook"]
    mapped = REASON_MAP[reason]

    def fill(value):
        if isinstance(value, str):
            return value.format(temperature=temperature, **mapped)
        return value

    payload = {k: fill(v) for k, v in webhook["payload"].items()}
    return webhook["method"].upper(), webhook["url"], webhook.get("headers", {}), payload


last_webhook_time = 0


def call_webhook(cfg, reason, temperature):
    global last_webhook_time
    cooldown = cfg["webhook"].get("cooldown", 900)
    if time.time() - last_webhook_time < cooldown:
        remaining = int(cooldown - (time.time() - last_webhook_time))
        print(f"Webhook skipped — cooldown active ({remaining}s remaining)")
        return

    method, url, headers, payload = build_request(cfg, reason, temperature)
    try:
        response = requests.request(method, url, headers=headers, json=payload, timeout=10)
        print(f"Webhook called: {response.status_code}")
        if response.ok:
            last_webhook_time = time.time()
        else:
            print(f"Webhook error: {response.text}")
    except requests.RequestException as e:
        print(f"Webhook failed: {e}")


def main():
    cfg = load_config()

    port = cfg["serial"]["port"]
    if port == "auto":
        port = find_pico_port()
        print(f"Found Pico on {port}")

    print(f"Listening on {port}...")
    with serial.Serial(port, cfg["serial"]["baud_rate"], timeout=1) as ser:
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            print(line)
            try:
                temperature = float(line.replace("°C", ""))
                reason = check_thresholds(cfg, temperature)
                if reason:
                    call_webhook(cfg, reason, temperature)
            except ValueError:
                pass


if __name__ == "__main__":
    main()
