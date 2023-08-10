import jwt
from jwt.exceptions import InvalidSignatureError
import jose


class TokenVerifier:
    def detect_base64(self,content:str)->(bool,str):
        import base64
        import binascii

        try:
            ret = base64.b64decode(content,validate=True)
            return True,ret.decode('utf8')
        except binascii.Error:
            return False,None
    def verify(self, share_key: str, token: str) -> dict:
        try:
            decoded = jwt.decode(token, share_key, options={
                "verify_exp": False,
                "verify_aud": False
            })
            return decoded
        except jwt.exceptions.DecodeError as e:
            return None
        except jwt.exceptions.InvalidSignatureError as e:
            return None
    def serilize_token(self,token):
        is_base64, raw_content = self.detect_base64(token)
        if is_base64:
            import json
            try:
                ret= json.loads(raw_content)
                return ret
            except Exception as e:

                decoded = jwt.decode(raw_content, options={
                    "verify_exp": False,
                    "verify_aud": False
                }, algorithms="SH256")
                return decoded
        else:
            decoded = jwt.decode(token,  options={
                "verify_exp": False,
                "verify_aud": False
            },algorithms="SH256")
            return decoded
# import cy_kit
# fx= cy_kit.singleton(TokenVerifier)
# token="eyJ1c2VySUQiOiJBRE1JTiIsImJ1aWQiOiJHdWVzdCIsImxhbmd1YWdlIjoiVk4iLCJ0aGVtZSI6ImRlZmF1bHR8bGlnaHQiLCJkZWZhdWx0SG9tZSI6IjEiLCJ0ZW5hbnQiOiJkZWZhdWx0IiwiZG9tYWluIjpudWxsLCJjb25uZWN0aW9uTmFtZSI6IkVSTV9TeXN0ZW0iLCJzZWN1cml0eUtleSI6IjMwZjRmYzFkLWViNjYtNGZjMC04Y2U5LTFlNDA2NjE3MjZhMyIsInRva2VuIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SjFibWx4ZFdWZmJtRnRaU0k2SWtGRVRVbE9JaXdpYm1GdFpXbGtJam9pUVVSTlNVNGlMQ0psYldGcGJDSTZJbXh3YUhSb2RXOXVaMEJzWVdOMmFXVjBMbU52YlM1MmJqRWlMQ0pHZFd4c1RtRnRaU0k2SWt6RHFpQlFhT0c2b1cwZ1NHX0RvR2tnVkdqR3NNYWhibWNpTENKRmJXRnBiQ0k2SW14d2FIUm9kVzl1WjBCc1lXTjJhV1YwTG1OdmJTNTJiakVpTENKTmIySnBiR1VpT2lJeU1UQXlNak13T0RRNUlpd2lhblJwSWpvaVl6WXdZVEU1WVRJdFkyRXhZUzAwWVRFeExUZ3dZamd0TTJGaVpUTTNabVV5TmpobUlpd2ljMnNpT2lJek1HWTBabU14WkMxbFlqWTJMVFJtWXpBdE9HTmxPUzB4WlRRd05qWXhOekkyWVRNaUxDSnVZbVlpT2pFMk9ERTNPREEzT0RVc0ltVjRjQ0k2TVRZNE1UZzJOekU0TlN3aWFXRjBJam94TmpneE56Z3dOemcxTENKcGMzTWlPaUpsY20wdWJHRmpkbWxsZEM1MmJpSXNJbUYxWkNJNkltVnliUzVzWVdOMmFXVjBMblp1SW4wLmtSVnl6VGZOSGFjVk4ydW44M3RXMWpvaUVaZmdMWmlSaDFvQmZfWExsZEEiLCJyZWZyZXNoVG9rZW4iOiJTRlJOS0k1RVVRR082SEM3QkE5RUtMM0RBNFkwMVdVUlY5SWI3ZDA3NDlhLTNhMTgtNGE0Ny04MThhLTgyZjMxNDAxY2VmZiIsImV4cGlyZU9uIjoiMjAyMy0wNC0xOVQwMToxOTo0NS43MjEwMTY0WiIsInNlc3Npb25UaW1lb3V0IjowLCJnZW5kZXIiOm51bGwsImZpcnN0TmFtZSI6bnVsbCwibWlkZGxlTmFtZSI6bnVsbCwibGFzdE5hbWUiOm51bGwsInVzZXJOYW1lIjoiTMOqIFBo4bqhbSBIb8OgaSBUaMawxqFuZyIsIm1vYmlsZSI6IjIxMDIyMzA4NDkiLCJlbWFpbCI6ImxwaHRodW9uZ0BsYWN2aWV0LmNvbS52bjEiLCJhdmF0YXIiOm51bGwsImFkbWluaXN0cmF0b3IiOnRydWUsImZ1bmN0aW9uQWRtaW4iOnRydWUsInN5c3RlbUFkbWluIjp0cnVlLCJjYW50Q2hhbmdlUFciOmZhbHNlLCJsb2NrZWQiOmZhbHNlLCJncm91cElEIjpudWxsLCJsb2dvbiI6IjIwMjMtMDQtMTdUMTg6MTk6NDYuMTMyODk5LTA3OjAwIiwibmV2ZXJFeHBpcmUiOmZhbHNlLCJlbXBsb3llZSI6bnVsbH0="
# pub_key = "A8D3F5D1A91944445CB61358CA999-LV@2020-8D16AB267DBABFD3BB94223791914"
# cx= fx.serilize_token(token)
#
# token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImVlYTFiMWY0MjgwN2E4Y2MxMzZhMDNhM2MxNmQyOWRiODI5NmRhZjAiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIxNjcwMzExMDQ1NjYtYmZpMmgyODdzMWYxdTFzaWFicGI1ZWo4OHExa25nMnMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIxNjcwMzExMDQ1NjYtYmZpMmgyODdzMWYxdTFzaWFicGI1ZWo4OHExa25nMnMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDEyODA4NDEwNzU2MjUwMzQwMjAiLCJlbWFpbCI6ImRzYjMyMW1wQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdF9oYXNoIjoiWmpVY1Eyd3JkLUdzY3F2Y2dqci1BQSIsIm5vbmNlIjoiUFp2SGhsX2tUTGR1Sktmem80LW9qdyIsImlhdCI6MTYxMTY5MjA2NywiZXhwIjoxNjExNjk1NjY3fQ.kNFbqjtJO2HKsSX-jt967MLi2xjeRH4W9JsA4yPQDQEgrHqa3BX6PVFJCBjq-Fn7vmlTT1lUcElVPwtvcBUV8Z4I7dCuWKcTxTt6R8501f1I2X0tQeEu_zfg-ianzOlQkg3KvLT_D-oaIfNkoU7jAt4Mywe6xHiDKszlA6KE8T6PLV_VeiCJGvciLbPW7DhKiuL-kfTjhHoZ6_XHeruR6rb_psZNvH5t-D3Yjc27EwH0_Wumcl1GjN20eF2xO-UDhO4BMRHGIM5876QUYB58dxblLG1flEaeXi9z4R-XnrLPYpAYZDYQDcPMni9fUm9d8pNZDeTGh6WyGkTqkXuHvg"
#
# # Insecure - doesn't validate the token.
# # decoded = jwt.decode(token, options={"verify_signature": False})
#
# # Optional, not sure if if this increases security
# # url = "https://www.googleapis.com/oauth2/v3/certs"
#
# # pub_key = client.get_signing_key_from_jwt(token).key
# pub_key = "A8D3F5D1A91944445CB61358CA999-LV@2020-8D16AB267DBABFD3BB94223791914"
# token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IkNPRFhBRE1JTiIsIm5hbWVpZCI6IkNPRFhBRE1JTiIsImVtYWlsIjoiaW5mb0Bjb2R4LnZuIiwiRnVsbE5hbWUiOiJBZG1pbmlzdHJhdG9yIiwiRW1haWwiOiJpbmZvQGNvZHgudm4iLCJNb2JpbGUiOiIxMjM2NTQiLCJqdGkiOiIzNWI1YmYyOC1iNzUyLTQ2NzYtOGE1ZC04NmE4Njc4ZTBkYjQiLCJzayI6ImZiOGYyM2E5LTEwZTctNGUxMi1iYWFiLTY3ODEzNDc1OTBhYyIsIm5iZiI6MTY4MTQzNzExMSwiZXhwIjoxNzEyOTczMTExLCJpYXQiOjE2ODE0MzcxMTEsImlzcyI6ImVybS5sYWN2aWV0LnZuIiwiYXVkIjoiZXJtLmxhY3ZpZXQudm4ifQ.CIeeKwssILojUv_jH11nXryXBsEIQPKKl3Zq8XaY73A"
#
#
# # aud = jwt.decode(token, options={"verify_signature": False})["aud"]
# # decoded = jwt.decode(token, pub_key, algorithms=["RS256"], options={"verify_exp": True})
#
# token2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJvb3QiLCJhcHBsaWNhdGlvbiI6ImFkbWluIn0.u2AAtdLy3sb3kfZnmIt7t9-1mhYqnb3rLGMykGQNiSg"
# token3 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IkFETUlOIiwibmFtZWlkIjoiQURNSU4iLCJlbWFpbCI6ImxwaHRodW9uZ0BsYWN2aWV0LmNvbS52bjEiLCJGdWxsTmFtZSI6IkzDqiBQaOG6oW0gSG_DoGkgVGjGsMahbmciLCJFbWFpbCI6ImxwaHRodW9uZ0BsYWN2aWV0LmNvbS52bjEiLCJNb2JpbGUiOiIyMTAyMjMwODQ5IiwianRpIjoiZDEwNmI4Y2ItNTc2My00MDlhLThhYjItZDhkYjcxNWNkM2E4Iiwic2siOiIxMjE0ZTJjOS04MmUwLTQ0YzAtOGVkYy01YjEwNGI2NDY4YTUiLCJuYmYiOjE2ODE3MDYwMTUsImV4cCI6MTY4MTc5MjQxNSwiaWF0IjoxNjgxNzA2MDE1LCJpc3MiOiJlcm0ubGFjdmlldC52biIsImF1ZCI6ImVybS5sYWN2aWV0LnZuIn0.7L8GLnNa6EfE3slbWzxlEC6Ta9677LX3MMZXIHVmCbI"
# # aud = jwt.decode(token,verify=False)["aud"]
# # decoded = jwt.decode(token3, pub_key, options={
# #     "verify_exp": False,
# #     "verify_aud": False
# # })
# # decoded=jwt.decode(encoded, key, algorithms="HS256")
# cx = fx.verify(pub_key,token=token2)
# print(cx)
