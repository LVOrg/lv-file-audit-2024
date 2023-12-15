from datetime import datetime, timedelta
from jose import jwt
AUDIENCE = "https://officewopi.azurewebsites.net"
def generate_token(user, container, doc_id):
  now = datetime.utcnow()
  signing_key = get_signing_key()  # Replace with your key retrieval logic

  # Define claims
  claims = {
    "name": user,
    "container": container,
    "docid": doc_id,
    "exp": (now + timedelta(hours=1)).timestamp(),  # Expiration time
    "iss": AUDIENCE,  # Issuer
    "aud": AUDIENCE,  # Audience
  }

  # Generate token
  token = jwt.encode(claims, signing_key, algorithm="RS256")
  return token

# Replace these with your actual functions
def get_signing_key(tenant_id:str=None,client_id:str=None,client_secret:str=None):
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    # Replace with your Azure AD tenant ID, client ID, and secret
    tenant_id = "13a53f39-4b4d-4268-8c5e-ae6260178923"
    client_id = "553ae3ba-037a-4fc4-bd8e-368b06692c06"
    client_secret = "bfs8Q~ANxTS0oIoqxywpriBMDg.aUyoIidQthdjJ"
    credential = DefaultAzureCredential()
    key_vault_url = "https://your-key-vault.vault.azure.net"
    key_vault_url ="https://dev.vault.azure.net"
    key_vault_client = SecretClient(vault_url=key_vault_url, credential=credential)

    # Get the signing key from Azure Key Vault
    key_name = "your-signing-key-name"
    key_name ="nttlong"
    key_secret = key_vault_client.get_secret(key_name).value
    return key_secret

