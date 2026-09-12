def detect_vendor(config_text):
    """
    Detect network device vendor from configuration text.

    Supported vendors:
    - Fortinet
    - Palo Alto
    - Juniper
    - Cisco
    - Arista
    - Check Point
    """

    if not config_text:
        return "Unknown"

    config = config_text.lower()

    # -------------------------------------------------
    # Fortinet
    # -------------------------------------------------
    if (
        "config system global" in config
        or "config system interface" in config
        or "config firewall policy" in config
        or "fortigate" in config
        or "fortios" in config
    ):
        return "Fortinet"

    # -------------------------------------------------
    # Palo Alto
    # -------------------------------------------------
    elif (
        "pan-os" in config
        or "palo alto" in config
        or "paloalto" in config
        or "<deviceconfig>" in config
        or "<network>" in config and "<devices>" in config
    ):
        return "Palo Alto"

    # -------------------------------------------------
    # Juniper
    # -------------------------------------------------
    elif (
        "set system services ssh" in config
        or "set system host-name" in config
        or "set interfaces ge-" in config
        or "set interfaces xe-" in config
        or "junos" in config
        or "juniper" in config
    ):
        return "Juniper"

    # -------------------------------------------------
    # Arista
    # -------------------------------------------------
    elif (
        "arista" in config
        or "eos" in config
        or "management api http-commands" in config
        or "daemon terminattr" in config
    ):
        return "Arista"

    # -------------------------------------------------
    # Check Point
    # -------------------------------------------------
    elif (
        "check point" in config
        or "checkpoint" in config
        or "gaia" in config
        or "clish" in config
        or "set expert-password" in config
    ):
        return "Check Point"

    # -------------------------------------------------
    # Cisco
    # -------------------------------------------------
    elif (
        "cisco" in config
        or "line vty" in config
        or "version 15." in config
        or "version 16." in config
        or "version 17." in config
        or "hostname " in config
        and (
            "interface gigabitethernet" in config
            or "interface fastethernet" in config
            or "router ospf" in config
            or "router bgp" in config
        )
    ):
        return "Cisco"

    # -------------------------------------------------
    # Unknown
    # -------------------------------------------------
    else:
        return "Unknown"