
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var appEditView = await View(import.meta, class EditAppView extends BaseScope {
    app = {
        Apps:{
            Azure: {}
        }
    }
    onInit() {
//        this.doEditApp(getPaths()[2])
    }
    async doEditApp(appName) {
        this.clientSecretInputType='password'
        var me=this;
        me.app = await api.post(`admin/apps/get`, {
            AppName: appName
        })
        if((!me.app.Apps)||(me.app.Apps==null)){
            me.app.Apps= {
                Azure:{
                    Name: null
                }
            }
        }
        me.$applyAsync();
    }
    async doNewApp() {
        this.app = {}
        this.clientSecretInputType='password'
        this.$applyAsync();
    }
    clientSecretOnOff(){
        if (this.clientSecretInputType=='password'){
            this.clientSecretInputType='text'
            this.$applyAsync();
        }
        else {
            this.clientSecretInputType='password'
            this.$applyAsync();
        }
    }
    async doUpdateApp() {
        debugger;
        var me = this;
//        var logoFiles = me.$elements.find("#logo")[0].files;
//        var logoFile = undefined
//        if (logoFiles.length > 0) {
//            logoFile = logoFiles[0];
//        }
        if ((!me.app)||(!me.app.AppId)||(me.app.AppId==null)){
            var ret = await api.post(`apps/admin/register`, {
                Data:{
                    Name: me.app.Name,
                    Token: window.token,
                    LoginUrl: me.app.LoginUrl,
                    ReturnUrlAfterSignIn: me.app.ReturnUrlAfterSignIn,
                    Description: me.app.Description,
                    Domain: me.app.Domain,
                    Apps: me.app.Apps
                }
            });
            if (ret.error) {
                msgError(ret.error.message)
            }
        }
        else {
            var ret = await api.post(`admin/apps/update/${me.app.Name}`, {
                Data: {
                    Name: me.app.Name,
                    Token: window.token,
                    LoginUrl: me.app.LoginUrl,
                    ReturnUrlAfterSignIn: me.app.ReturnUrlAfterSignIn,
                    Description: me.app.Description,
                    Domain: me.app.Domain,
                    Apps: me.app.Apps
                }
            });
            if (ret.error) {
                msgError(ret.error.message)
            }
        }
    }
    async getListOfApps() {
        

    }

});
export default appEditView;