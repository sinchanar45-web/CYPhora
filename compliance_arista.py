def check_arista_compliance(config_text):

    results = []

    config = config_text.lower()

    # Check 1: SSH
    if "management ssh" in config or "management api ssh" in config:
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

    # Check 2: HTTP Server
    if "no management api http-commands" in config:
        results.append({
            "check": "HTTP Management",
            "status": "PASS",
            "severity": "LOW",
            "message": "HTTP management access is disabled."
        })
    else:
        results.append({
            "check": "HTTP Management",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "HTTP management access is not explicitly disabled."
        })

    # Check 3: Logging
    if "logging buffered" in config or "logging host" in config:
        results.append({
            "check": "Logging",
            "status": "PASS",
            "severity": "LOW",
            "message": "System logging is configured."
        })
    else:
        results.append({
            "check": "Logging",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "System logging is not configured."
        })

    # Check 4: NTP
    if "ntp server" in config:
        results.append({
            "check": "NTP Configuration",
            "status": "PASS",
            "severity": "LOW",
            "message": "NTP server is configured."
        })
    else:
        results.append({
            "check": "NTP Configuration",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "NTP server is not configured."
        })

    return results