from jose import jwt
import cy_kit
from cy_fucking_whore_microsoft.fucking_wopi.settings_helper import SettingService
import datetime


class WopiSecurity:
    def __init__(self, setting_service=cy_kit.singleton(SettingService)):
        self.setting_service = setting_service

    def validate_token(self, app_name: str, token_string: str, container: str, doc_id: str) -> bool:
        """
        Validates a JWT token and checks if it contains claims for the specified container and document ID.

        Args:
            token_string: The JWT token string.
            container: The expected container claim value.
            doc_id: The expected document ID claim value.

        Returns:
            True if the token is valid and contains the expected claims, False otherwise.
            :param app_name:
        """
        setting = self.setting_service.get_setting(
            app_name=app_name
        )
        try:

            # Define the JWT validation parameters
            token_validation_parameters = {
                "audience": setting.audience,
                "issuer": setting.issuer,
                "algorithms": ["RS256"],
            }
            token = jwt.decode(token_string, setting.secret_key, algorithms=["RS256"],
                               options=token_validation_parameters)
            return (
                    token.get("container") == container
                    and token.get("docid") == doc_id
            )
        except Exception:
            return False

    def get_user_from_token(self, app_name: str, token_string: str) -> str:
        """
        Extracts the user identifier from a JWT token.

        Args:
            token_string: The JWT token string.

        Returns:
            The user identifier if the token is valid, an empty string otherwise.
            :param token_string:
            :param app_name:
        """
        setting = self.setting_service.get_setting(
            app_name=app_name
        )
        try:
            # Define the JWT validation parameters
            token_validation_parameters = {
                "audience": setting.audience,
                "issuer": setting.issuer,
                "algorithms": ["RS256"],
            }
            token = jwt.decode(token_string, setting.secret_key, algorithms=["RS256"],
                               options=token_validation_parameters)
            return token.get("user_id", "")
        except Exception:
            return ""

    def generate_token(self, app_name: str, user: str, container: str, doc_id: str) -> str:
        """
        Generates a JWT token with user, container, and document ID claims.

        Args:
            user: The user identifier.
            container: The container claim value.
            doc_id: The document ID claim value.

        Returns:
            The generated JWT token as a string.
        """

        now = datetime.datetime.utcnow()
        payload = {
            "sub": user,
            "container": container,
            "docid": doc_id,
            "iat": now,
            "exp": now + datetime.timedelta(hours=1),
        }
        setting = self.setting_service.get_setting(
            app_name=app_name
        )
        return jwt.encode(
            payload,
            setting.secret_key,
            algorithm="RS256",
            audience=setting.audience,
            issuer=setting.audience,
        )
