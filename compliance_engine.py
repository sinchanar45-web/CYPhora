def check_cisco_compliance(config_text):

    results = []

    config = config_text.lower()

    # Check 1: SSH Version 2
    if "ip ssh version 2" in config:
        results.append({
            "check": "SSH Version 2",
            "status": "PASS",
            "severity": "LOW",
            "message": "SSH Version 2 is enabled."
        })
    else:
        results.append({
            "check": "SSH Version 2",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "SSH Version 2 is not explicitly configured."
        })

    # Check 2: HTTP Server
    if "no ip http server" in config:
        results.append({
            "check": "HTTP Server",
            "status": "PASS",
            "severity": "LOW",
            "message": "HTTP server is disabled."
        })
    else:
        results.append({
            "check": "HTTP Server",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "HTTP server is not explicitly disabled."
        })

    # Check 3: Logging
    if "logging buffered" in config:
        results.append({
            "check": "Logging",
            "status": "PASS",
            "severity": "LOW",
            "message": "Buffered logging is configured."
        })
    else:
        results.append({
            "check": "Logging",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "Buffered logging is not configured."
        })

    # Check 4: SSH-only Remote Access
    if "transport input ssh" in config:
        results.append({
            "check": "Remote Access",
            "status": "PASS",
            "severity": "LOW",
            "message": "SSH-only remote access is configured."
        })
    else:
        results.append({
            "check": "Remote Access",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "SSH-only remote access is not configured."
        })

    # Check 5: NTP
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