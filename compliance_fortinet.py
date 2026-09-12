def check_fortinet_compliance(config_text):

    results = []

    config = config_text.lower()

    # Check 1: HTTPS Administration
    if "set admin-sport" in config:
        results.append({
            "check": "HTTPS Administration",
            "status": "PASS",
            "severity": "LOW",
            "message": "Administrative HTTPS configuration is present."
        })
    else:
        results.append({
            "check": "HTTPS Administration",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "Administrative HTTPS configuration is not detected."
        })

    # Check 2: Logging
    if "set status enable" in config:
        results.append({
            "check": "Logging",
            "status": "PASS",
            "severity": "LOW",
            "message": "Logging is enabled."
        })
    else:
        results.append({
            "check": "Logging",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "Logging is not enabled."
        })

    # Check 3: NTP
    if "config system ntp" in config:
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