BUSINESS_USER = "<IsLicensedUser=BUSINESS_USER&>"
DC_LLCC = "<rs=DC_LLCC&>"
DISABLE_ASYNC = "<na=DISABLE_ASYNC&>"
DISABLE_CHAT = "<dchat=DISABLE_CHAT&>"
DISABLE_BROADCAST = "<vp=DISABLE_BROADCAST&>"
EMBDDED = "<e=EMBEDDED&>"
FULLSCREEN = "<fs=FULLSCREEN&>"
PERFSTATS = "<showpagestats=PERFSTATS&>"
RECORDING = "<rec=RECORDING&>"
THEME_ID = "<thm=THEME_ID&>"
UI_LLCC = "<ui=UI_LLCC&>"
VALIDATOR_TEST_CATEGORY = "<testcategory=VALIDATOR_TEST_CATEGORY>"
placeholders = [
    BUSINESS_USER,
    DC_LLCC,
    DISABLE_ASYNC,
    DISABLE_CHAT,
    DISABLE_BROADCAST,
    EMBDDED,
    FULLSCREEN,
    PERFSTATS, RECORDING, THEME_ID, UI_LLCC, VALIDATOR_TEST_CATEGORY
]


def get_placeholder_value(placeholder):
    """
    Gets the value of the placeholder.

    Args:
        placeholder: The placeholder name.

    Returns:
        The placeholder value.
    """
    ph = placeholder[1:placeholder.find("=")+1]
    key = placeholder[placeholder.find("=") + 1:].rstrip('>').rstrip('&')
    result = ""
    switch = {
        "BUSINESS_USER": ph + "1",
        "DC_LLCC": ph + "1033",
        "UI_LLCC": ph + "1033",
        "DISABLE_ASYNC": ph + "true",
        "DISABLE_BROADCAST": ph + "true",
        "EMBEDDED": ph + "true",
        "FULLSCREEN": ph + "true",
        "RECORDING": ph + "true",
        "THEME_ID": ph + "true",
        "DISABLE_CHAT": ph + "false",
        "PERFSTATS": "",
        "VALIDATOR_TEST_CATEGORY": ph + "OfficeOnline",
    }
    result = switch.get(key)
    return result
