def check_juniper_compliance(config_text):

    results = []

    config = config_text.lower()

    # Check 1: SSH
    if "set system services ssh" in config:
        results.append({
            "check": "SSH Service",
            "status": "PASS",
            "severity": "LOW",
            "message": "SSH service is configured."
        })
    else:
        results.append({
            "check": "SSH Service",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "SSH service is not configured."
        })

    # Check 2: Telnet
    if "set system services telnet" not in config:
        results.append({
            "check": "Telnet Service",
            "status": "PASS",
            "severity": "LOW",
            "message": "Telnet service is not configured."
        })
    else:
        results.append({
            "check": "Telnet Service",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "Telnet service is configured and should be disabled."
        })

    # Check 3: System Logging
    if "set system syslog" in config:
        results.append({
            "check": "System Logging",
            "status": "PASS",
            "severity": "LOW",
            "message": "System logging is configured."
        })
    else:
        results.append({
            "check": "System Logging",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "System logging is not configured."
        })

    # Check 4: NTP
    if "set system ntp" in config:
        results.append({
            "check": "NTP Configuration",
            "status": "PASS",
            "severity": "LOW",
            "message": "NTP configuration is present."
        })
    else:
        results.append({
            "check": "NTP Configuration",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "NTP configuration is not detected."
        })

    return results