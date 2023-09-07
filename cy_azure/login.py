def get_user_from_token(access_token):
  """
  Get the user from the access token.

  Args:
    access_token: The access token.

  Returns:
    The user object.
  """

  # Set the TLS version to TLS 1.2.
  service_point_manager.SecurityProtocol = SecurityProtocolType.Tls12

  # Create a new HTTP client.
  with requests.Session() as client:
    # Set the Authorization header.
    client.headers["Authorization"] = f"Bearer {access_token}"

    # Make a GET request to the Microsoft Graph API.
    response = client.get("https://graph.microsoft.com/v1.0/me")

    # Get the user object from the response.
    user = json.loads(response.content)

    return user