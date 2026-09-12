def check_paloalto_compliance(config_text):

    results = []

    config = config_text.lower()

    # Check 1: Telnet disabled
    if "disable-telnet yes" in config:
        results.append({
            "check": "Telnet Service",
            "status": "PASS",
            "severity": "LOW",
            "message": "Telnet service is disabled."
        })
    else:
        results.append({
            "check": "Telnet Service",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "Telnet service is not explicitly disabled."
        })

    # Check 2: HTTP disabled
    if "disable-http yes" in config:
        results.append({
            "check": "HTTP Service",
            "status": "PASS",
            "severity": "LOW",
            "message": "HTTP service is disabled."
        })
    else:
        results.append({
            "check": "HTTP Service",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "HTTP service is not explicitly disabled."
        })

    # Check 3: NTP
    if "ntp-servers" in config:
        results.append({
            "check": "NTP Configuration",
            "status": "PASS",
            "severity": "LOW",
            "message": "NTP server configuration is present."
        })
    else:
        results.append({
            "check": "NTP Configuration",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "NTP configuration is not detected."
        })

    return results