
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var appEditView = await View(import.meta, class EditAppView extends BaseScope {
    app = {}
    onInit() {
        this.doEditApp(getPaths()[2])
    }
    async doEditApp(appName) {
        this.app = await api.post(`apps/admin/get`, {
            AppName: appName,
            Token: window.token
        })
        this.$applyAsync();
    }
    async doNewApp() {
        this.app = {}
        this.$applyAsync();
    }
    async doUpdateApp() {
        
        var me = this;
        var logoFiles = me.$elements.find("#logo")[0].files;
        var logoFile = undefined
        if (logoFiles.length > 0) {
            logoFile = logoFiles[0];
        }
        var ret = await api.post(`apps/admin/register`, {
            Name: me.app.Name,
            Token: window.token,
            LoginUrl: me.app.LoginUrl,
            ReturnUrlAfterSignIn: me.app.ReturnUrlAfterSignIn,
            Description: me.app.Description,
            Domain: me.app.Domain,
            LogoFile: logoFile
        });
        if (ret.error) {
            msgError(ret.error.message)
        }
    }
    async getListOfApps() {
        

    }

});
export default appEditView;