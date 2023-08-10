import { BaseScope, View } from "./../../js/ui/BaseScope.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var loginView = await View(import.meta, class LoginView extends BaseScope {
    
    async doLogin() {
        try {
            debugger;
            var me = this;
            me.data["language"] = me.data["language"] || "vn"
            var ret = await api.formPost(`accounts/token`, {
                username: `${me.data.username}`,
                password: me.data.password
            });
            api.storeAccessToken(ret.access_token);
            var sso_token = await api.post(`get_sso_token`, {});
            console.log(sso_token);
            if (window.location.href.indexOf('?ret=') > -1) {
                var retUrl = window.location.href.split('?ret=')[1].split('&')[0];
                window.location.href = `${api.getUrl()}/sso/signin/${sso_token.token}?ret=${retUrl}`;
            }
            else {
                var retUrl = decodeURIComponent(window.location.protocol + '//' + window.location.host);
                window.location.href = `${api.getUrl()}/sso/signin/${sso_token.token}?ret=${retUrl}`;
            }
        }
        catch (e) {
            msgError("Login fail");
        }
    }
    
});
export default loginView;