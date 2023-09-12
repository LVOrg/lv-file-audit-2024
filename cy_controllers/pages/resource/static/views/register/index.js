
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
import api from "../../js/ClientApi/api.js"
import { parseUrlParams, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var appEditView = await View(import.meta, class EditAppView extends BaseScope {
    app = {}
    isEdit = false
    app_name = undefined
    onInit() {
        var queryData = parseUrlParams();
        var app_name = queryData["app"]
        this.app_name = app_name
        if (app_name) {
            this.doEditApp(app_name)
        }
        else {
            this.app = {}
            this.$applyAsync();
        }
    }
    async doEditApp(appName) {
        

        this.app = await api.post(`admin/apps/get/${appName}`, {
            AppEdit: appName
        })
        this.isEdit = true;
        this.$applyAsync();
    }
    async doNewApp() {
        this.app = {}
        this.$applyAsync();
    }
    async doUpdateApp() {
        debugger;
        var me = this;
        var logoFiles = me.$elements.find("#logo")[0].files;
        var logoFile = undefined
        if (logoFiles.length > 0) {
            logoFile = logoFiles[0];
        }
        var ret = await api.post(`admin/apps/update/${this.app_name}`, {
            Data: me.app
        });
        if (ret.error) {
            msgError(ret.error.message)
        }
    }
    async doCreateApp() {
        debugger;
        var me = this;
        var logoFiles = me.$elements.find("#logo")[0].files;
        var logoFile = undefined
        if (logoFiles.length > 0) {
            logoFile = logoFiles[0];
        }
       
        var ret = await api.post(`admin/apps/register`, {
            Data: this.app
        })
        
        if (ret.Error) {
            msgError(ret.Error.Message)
        }
    }
    async getListOfApps() {
        

    }

});
export default appEditView;