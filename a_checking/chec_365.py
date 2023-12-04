from cy_azure import auth
access_token = auth.get_auth_token(
                    verify_code="M.C105_BAY.2.326190f4-c20a-4835-43b8-bf86403be536",
                    redirect_uri="https://172.16.13.72:8012/lvfile/api/lv-docs/azure/after_login",
                    tenant=  "13d23acb-69f3-4651-98fe-76e95992f779",
                    client_id="553ae3ba-037a-4fc4-bd8e-368b06692c06",
                    client_secret= "_go8Q~Z1ykBdxAxiO7XvW1dyKp11HtmyjhDhMcn3"

                )
print(access_token)