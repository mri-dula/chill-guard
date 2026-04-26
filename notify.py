def alert(reason, temperature):
    """
    Called when temperature is out of range.
    reason: "too_cold" or "too_hot"
    temperature: current reading in °C
    """
    # TODO: implement janitor notification (SMS, call, email, etc.)
    print(f"ALERT [{reason}]: {temperature:.1f}°C — janitor notification not yet configured")
