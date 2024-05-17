import requests
import rsa.key
import xmltodict
from cy_wopi_util.models import WopiAction, FileModel

"""
 <add key="WopiDiscovery" value="https://onenote.officeapps-df.live.com/hosting/discovery"/>
"""
wopi_discovery = "https://onenote.officeapps-df.live.com/hosting/discovery"
import wopi_url_placeholders

def get_discovery_info():
    res = requests.get(wopi_discovery)
    if res.status_code == 200:
        ret = xmltodict.parse(res.text)
        return ret
    else:
        raise Exception(f"get {wopi_discovery} was fail")


def get_action_url(action: WopiAction, file: FileModel, authority: str):
    urlsrc = action.urlsrc
    ph_cnt = 0
    for p in wopi_url_placeholders.placeholders:
        if p in urlsrc:
            ph = wopi_url_placeholders.get_placeholder_value(p)
            if ph:
                urlsrc = urlsrc.replace(p, ph + "&")
                ph_cnt += 1
            else:
                urlsrc = urlsrc.replace(p, ph)
    urlsrc += ("" if ph_cnt > 0 else "?") + f"WOPISrc=https://{authority}/wopi/files/{file.id}"
    return urlsrc
from cy_wopi_util import wopi_request_headers
import base64
__cache_proof__ = dict()
class WopiProof:
    oldvalue:str
    oldmodulus:str
    oldexponent:str
    value:str
    modulus:str
    exponent:str


def get_wopi_proof(context):
  """
  Get the WOPI proof from the cache or from the WOPI discovery service.

  Args:
    context: The HTTP context.

  Returns:
    The WOPI proof.
  """

  wopi_proof = None

  # Check the cache for the WOPI proof.

  if __cache_proof__.get("WopiProof"):
    wopi_proof = __cache_proof__.get("WopiProof")
  else:
    # Get the WOPI discovery document.

    response = requests.get(context.config["WopiDiscovery"])

    if response.status_code == 200:
      # Parse the WOPI discovery document.
      discovery_xml = xmltodict.parse(response.text)

      # Get the WOPI proof from the discovery document.
      proof = discovery_xml.get("proof-key")
      wopi_proof = WopiProof(
        value=proof.attrib["value"],
        modulus=proof.attrib["modulus"],
        exponent=proof.attrib["exponent"],
        oldvalue=proof.attrib["oldvalue"],
        oldmodulus=proof.attrib["oldmodulus"],
        oldexponent=proof.attrib["oldexponent"]
      )
      __cache_proof__["WopiProof"] = wopi_proof

      # Add the WOPI proof to the cache.


  return wopi_proof
def verify_proof(expected_proof, proof_from_request, proof_from_discovery):
    public_key = rsa.key.AbstractKey.load_pkcs1(base64.b64decode(proof_from_discovery))
    return public_key.verify(expected_proof, base64.b64decode(proof_from_request), "SHA256")

def validate_wopi_proof(context):
    if context.request.headers.get(wopi_request_headers.PROOF) is None or \
            context.request.headers.get(wopi_request_headers.TIME_STAMP) is None:
        return False
    request_proof = context.request.headers.get(wopi_request_headers.PROOF)
    request_proof_old = ""
    if context.request.headers.get(wopi_request_headers.PROOF_OLD) is not None:
        request_proof_old = context.request.headers.get(wopi_request_headers.PROOF_OLD)

    # Get the WOPI proof info from discovery
    disco_proof =  get_wopi_proof(context)
    access_token_bytes = context.request.query_params["access_token"].encode("utf-8")
    host_url = context.request.url.original_string.replace(":44300", "").replace(":443", "")
    host_url_bytes = host_url.upper().encode("utf-8")
    time_stamp_bytes = (int(context.request.headers.get(wopi_request_headers.TIME_STAMP))
                        ).to_bytes(8, byteorder="big").reverse()
    expected = bytearray(
        4 + len(access_token_bytes) +
        4 + len(host_url_bytes) +
        4 + len(time_stamp_bytes))
    expected.extend(access_token_bytes.len().to_bytes(4, byteorder="big").reverse())
    expected.extend(access_token_bytes)
    expected.extend(host_url_bytes.len().to_bytes(4, byteorder="big").reverse())
    expected.extend(host_url_bytes)
    expected.extend(time_stamp_bytes.len().to_bytes(4, byteorder="big").reverse())
    expected.extend(time_stamp_bytes)
    expected_bytes = expected.tobytes()
    result1 = verify_proof(expected_bytes, request_proof, disco_proof.value)
    result2 = verify_proof(expected_bytes, request_proof, disco_proof.oldvalue)
    result3 = verify_proof(expected_bytes, request_proof_old, disco_proof.value)

    # Return the result of the first function that returned True

    return result1 or result2 or result3