from cy_azure.fwcking_auth import urls_auth, scopes
client_id="ddc68538-1f19-4202-87af-412a800fa965"
secret_value = "_go8Q~Z1ykBdxAxiO7XvW1dyKp11HtmyjhDhMcn3"
secret_value='unu8Q~lgs8hB2nIAvhHabMdgAGzDyEtTvGc64c~k'
tanent_id="13a53f39-4b4d-4268-8c5e-ae6260178923"
client_id="553ae3ba-037a-4fc4-bd8e-368b06692c06"
secret_value="_go8Q~Z1ykBdxAxiO7XvW1dyKp11HtmyjhDhMcn3"
token,_scopes = urls_auth.get_access_token_key_by_username_pass(
    client_id=client_id,
    tenant_id=tanent_id,
    secret_value=secret_value,
    scopes=scopes.get_one_drive(),
    # username="dev-test@nttlonglacvietcom.onmicrosoft.com",
    username="test-001@nttlonglacvietcom.onmicrosoft.com",
    password="L/\cviet2023"
)
print(token)

token2= urls_auth.accquire_access_token_key_token (
client_id=client_id,
    tenant_id=tanent_id,
    secret_value=secret_value,
    scopes=scopes.get_one_drive()

)


