import cy_kit
from cyx.ms.ms_services import MSService
ms_svc = cy_kit.singleton(MSService)
"""
ms-client-id: 0e205aee-0968-42a0-b4dc-702863d332f4
ms-secret-id: r5T8Q~RuU~6pgOHeOTg_p.ts8IIJf7-UQtoOCbe7
ms-tenant: 13a53f39-4b4d-4268-8c5e-ae6260178923 #13a53f39-4b4d-4268-8c5e-ae6260178923
"""
ms_client_id= "fc14c09c-2674-4ff5-a6e7-d3d0030abd57" #0e205aee-0968-42a0-b4dc-702863d332f4 #00000002-0000-0ff1-ce00-000000000000
ms_secret_id = "nZX8Q~22RwpUKvR~fR6x9c8xRgYWsh0VUZcbjcLe"
ms_tenant= "13a53f39-4b4d-4268-8c5e-ae6260178923"

token,roles = ms_svc.get_access_token_and_roles(
    client_secret=ms_secret_id,
    client_id=ms_client_id,
    tenant_id=ms_tenant,
    #scope=['https://outlook.office.com/Mail.Read","/.default'],
    # scope= ["https://outlook.office.com/Mail.Read/.default"]
    # scope= ["https://graph.microsoft.com/User.Read/.default"]
)
ms_svc.get_emails(token)
print(token)