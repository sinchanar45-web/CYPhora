def check_checkpoint_compliance(config_text):

    results = []

    config = config_text.lower()

    # Check 1: SSH
    if "ssh" in config:
        results.append({
            "check": "SSH Service",
            "status": "PASS",
            "severity": "LOW",
            "message": "SSH management access is configured."
        })
    else:
        results.append({
            "check": "SSH Service",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "SSH management access is not detected."
        })

    # Check 2: Telnet
    if "telnet" not in config:
        results.append({
            "check": "Telnet Service",
            "status": "PASS",
            "severity": "LOW",
            "message": "Telnet service is not detected."
        })
    else:
        results.append({
            "check": "Telnet Service",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "Telnet service is detected and should be disabled."
        })

    # Check 3: Logging
    if "log" in config:
        results.append({
            "check": "Logging",
            "status": "PASS",
            "severity": "LOW",
            "message": "Logging configuration is detected."
        })
    else:
        results.append({
            "check": "Logging",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "Logging configuration is not detected."
        })

    # Check 4: NTP
    if "ntp" in config:
        results.append({
            "check": "NTP Configuration",
            "status": "PASS",
            "severity": "LOW",
            "message": "NTP configuration is detected."
        })
    else:
        results.append({
            "check": "NTP Configuration",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "NTP configuration is not detected."
        })

    return results