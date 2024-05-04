data ={
    'ClientId': '816b4f31-0eaf-4f3a-a9fa-218144c9ef7d',
    'TenantId': '13a53f39-4b4d-4268-8c5e-ae6260178923',
    'ClientSecret': 'PsX8Q~mSyJZhB1ZOcQQyjMqltD1FWe65VLPZ0ayF',
    'RedirectUrl': 'https://docker.lacviet.vn/lvfile/api/lv-docs/after-ms-login'
}

from azure.identity.aio import ClientSecretCredential
credential = ClientSecretCredential('13a53f39-4b4d-4268-8c5e-ae6260178923',
                                    '816b4f31-0eaf-4f3a-a9fa-218144c9ef7d',
                                    'PsX8Q~mSyJZhB1ZOcQQyjMqltD1FWe65VLPZ0ayF')
t_credentials = ('816b4f31-0eaf-4f3a-a9fa-218144c9ef7d', 'PsX8Q~mSyJZhB1ZOcQQyjMqltD1FWe65VLPZ0ayF')

async def test():

    from msgraph import GraphServiceClient
    from O365 import Account
    account = Account(t_credentials)
    if not account.is_authenticated:  # will check if there is a token and has not expired
        # ask for a login
        # console based authentication See Authentication for other flows
        account.authenticate(scopes=scopes)
    m = account.new_message()
    m.to.add('nttlong@lacviet.com.vn')
    m.subject = 'Testing!'
    m.body = "George Best quote: I've stopped drinking, but only while I'm asleep."
    m.send()
    client = GraphServiceClient(credentials=credential, scopes=["https://graph.microsoft.com/.default"])
    # user = await client.users.by_user_id('userPrincipalName').get()
    users = await client.users.get()
    result = await client.me.drive.get()
import asyncio
if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)  # Set the event loop (optional)

  try:
    result = loop.run_until_complete(test())  # Call the async function
    # Process the result here (if any)
  except Exception as e:
    print(f"Error: {e}")
  finally:
    loop.close()  # Close the event loop