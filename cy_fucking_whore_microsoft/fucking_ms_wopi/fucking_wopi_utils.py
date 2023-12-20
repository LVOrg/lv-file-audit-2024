import base64
import urllib.parse



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
HOST_SESSION_ID = "<hid=HOST_SESSION_ID&>"
SESSION_CONTEXT = "<sc=SESSION_CONTEXT&>"
WOPISRC = "<wopisrc=WOPI_SOURCE&>"
ACTIVITY_NAVIGATION_ID = "<actnavid=ACTIVITY_NAVIGATION_ID&>"
placeholders = [
    BUSINESS_USER,
    DC_LLCC,
    DISABLE_ASYNC,
    DISABLE_CHAT,
    DISABLE_BROADCAST,
    EMBDDED,
    FULLSCREEN,
    PERFSTATS,
    RECORDING,
    THEME_ID,
    UI_LLCC,
    VALIDATOR_TEST_CATEGORY,
    HOST_SESSION_ID,
    SESSION_CONTEXT,
    WOPISRC,
    ACTIVITY_NAVIGATION_ID
]

fect_dict = dict(
    IsLicensedUser="1"
)


def get_placeholder_Value(placeholder):
    """
  Extracts and processes a value from a placeholder string.

  Args:
    placeholder: A string containing a placeholder with the format "<key=value>".

  Returns:
    The processed value associated with the key in the placeholder.
  """

    # Extract the key from the placeholder.
    key = placeholder[1:placeholder.index("=") + 1]

    # Initialize the result.
    result = ""
    if placeholder not in [
        BUSINESS_USER,
        DC_LLCC,
        UI_LLCC,
        DISABLE_ASYNC, DISABLE_BROADCAST, EMBDDED, FULLSCREEN, RECORDING, THEME_ID,
        HOST_SESSION_ID,
        SESSION_CONTEXT,
        WOPISRC,
        ACTIVITY_NAVIGATION_ID
    ]:
        return result
    # Handle different placeholder cases.
    if placeholder == BUSINESS_USER:
        result = key + "1"
    elif placeholder in (DC_LLCC, UI_LLCC):
        result = key + "1033"
    elif placeholder in (DISABLE_ASYNC, DISABLE_BROADCAST, EMBDDED, FULLSCREEN, RECORDING, THEME_ID):
        result = key + "true"
    elif placeholder == DISABLE_CHAT:
        result = key + "false"
    elif placeholder == PERFSTATS:
        # No processing needed for PERFSTATS.
        pass
    elif placeholder == VALIDATOR_TEST_CATEGORY:
        result = key + "all"  # Default value for test category
    return result


def get_action_url(urlsrc: str, wopi_src: str):
    """
  Generates a WOPI action URL based on the given action, file, and authority.

  Args:
    action: An object representing the WOPI action.
    file: An object representing the file.
    authority: The authority string (e.g., domain name).

  Returns:
    The generated WOPI action URL.
  """

    # Initialize the URL source.

    # Replace placeholders with processed values.
    ph_count = 0
    for placeholder in placeholders:
        if placeholder in urlsrc:
            placeholder_value = ""
            # placeholder_value = get_placeholder_Value(placeholder)
            if placeholder_value:
                urlsrc = urlsrc.replace(placeholder, f"{placeholder_value}&")
                ph_count += 1
            else:
                urlsrc = urlsrc.replace(placeholder, placeholder_value)

    # Add WOPISrc parameter to the end of the URL.
    if "?" in urlsrc:
        urlsrc += f"wopisrc={urllib.parse.quote_plus(wopi_src)}"
    else:
        urlsrc += f"?wopisrc={urllib.parse.quote_plus(wopi_src)}"

    return urlsrc


def generate_key(modulus_b64, exp_b64):
    """
    Generates an RSA public key given a base64-encoded modulus and exponent \n
    The fucking code came from
    https://learn.microsoft.com/en-us/microsoft-365/cloud-storage-partner-program/online/scenarios/proofkeys
    :param modulus_b64: base64-encoded modulus
    :param exp_b64: base64-encoded exponent
    :return: an RSA public key
    """
    from Crypto.PublicKey import RSA
    from rsa import asn1
    mod = int(base64.b64decode(modulus_b64).encode('hex'), 16)
    exp = int(base64.b64decode(exp_b64).encode('hex'), 16)
    seq = asn1.DerSequence()
    seq.append(mod)
    seq.append(exp)
    der = seq.encode()
    return RSA.importKey(der)
