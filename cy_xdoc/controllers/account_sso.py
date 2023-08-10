import cy_kit
import cy_web
import cy_xdoc.services.accounts
import cy_xdoc.services.apps
from cy_xdoc.auths import Authenticate
from fastapi import Depends
import uuid
from  fastapi import Request, Response

@cy_web.hanlder(method="post",path= "get_sso_token")
async def get_sso_token(request:Request,  token: str = Depends(Authenticate)):
    """
    <h2>Lấy SSO Token</h2>.<br>
    Bên cạnh việc cung cấp các Restfull API, hệ thống này cũng cung cấp các dịch vụ như xem file,
    media streaming,..., kể cả các web app.<br/>
    <p>
        Với các dịch vụ Restfull API thì việc truyền Access token vào header trước khi request về hệ thống này là rất dễ dàng.
        Nhưng với các dịch vụ khác là điều không thể.
        Ví dụ một request để xem video của một trang như sau: https://my-server/video/my-video.pm4
        đòi hỏi phải vượt qua được chứng thực tại server my-server
        (người dùng chỉ copy link này và paste vào thanh address của trình duyệt,
         nên việc gắn Access token vào request là điều không thể) Có các cách sau để vượt qua được chứng thực này:
        <ol>
            <li>Login (chỉ thực hiện được khi my-server cung cấp một trang để Login)</li>
            <li>
                Gắn query string vào link này ví dụ: https://my-server/video/my-video.pm4?access-token=... Điều này là không nên bởi 2 lý do sau
                <ol>
                    <li>Bảo mật: Access token là thành phần nên được che đậy cẩn thận </li>
                    <li>Url truy cập phải giống nhau với mọi user ở bất kỳ thời điểm nào </li>
                </ol>
            </li>
        </ol>
    </p>
    <p>
        Vì lý dó trên mà dịch vụ này sẽ cung cấp một API để lấy SSO Token. Sau đó sử dụng SSO Token này để Sigin vào dịch vụ
        (Dịch vụ không có quyền bắt người dùng cuối phải login)
    </p>
    <p>
        API này sẽ trả về SSO token key. SSO token sẽ mất hiệu lực ngay khi được sử dụng kể cả trường hợp không thành công.<br/>
        Để gọi API này gắn Access token vào header như sau:
        header[Authorization]='Bearer [Access token key]'<br/>
        Ví dụ:
        <textarea>

            fetch('api/get_sso_token', {
            method: 'POST',
            mode: 'no-cors', // this is to prevent browser from sending 'OPTIONS' method request first
            redirect: 'follow',
            headers: new Headers({
                    'Content-Type': 'text/plain',
                    'X-My-Custom-Header': 'value-v',
                    'Authorization': 'Bearer ' + token,
            }),
            body: companyName

        })
        </textarea>
    </p>

    :param app_name:
    :param token:
    :return:
    """
    if not hasattr(request,'application'):
        return Response(status_code=401)
    app_name = request.application
    if app_name is None:
        return Response(status_code=401)

    ret_url=cy_web.get_host_url()
    account_service = cy_kit.inject(cy_xdoc.services.accounts.AccountService)
    app_service = cy_kit.inject(cy_xdoc.services.apps.AppServices)
    if app_name!='admin':
        app_item = app_service.get_item('admin',app_name)
        ret_url = app_item.get("ReturnUrlAfterSignIn",cy_web.get_host_url())
    ret= account_service.create_sso_id(
        app_name='admin',
        token=token['token'],
        return_url=ret_url
    )
    # ret = await container.Services.accounts.create_sso_id_async(
    #     app_name='admin',
    #     token = token,
    #     return_url =ret_url
    #
    # )


    return {"token": ret}
