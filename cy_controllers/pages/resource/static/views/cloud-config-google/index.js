
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var googleConfig = await View(import.meta, class FilesView extends BaseScope {

    async init() {

        this.ui = {
            hasSelected: false
        }
        var queryData = parseUrlParams();
        var r = await this.$getElement();

        $(window).resize(() => {
            $(r).css({
                "max-height": $(document).height() - 100
            })
        })
        $(r).css({
            "max-height": $(document).height() - 100
        })
        this.$applyAsync();
        this.data = {}
        debugger;
    }
    async setInfoAsync(appName){
    //https://docker.lacviet.vn/lvfile/api/lv-docs/cloud/google-settings/get
        this.appName=appName
        this.data = await api.post(`${this.appName}/cloud/google-settings/get`, {
            Token: window.token
        });
        this.$applyAsync();
    }
    async getGoogleLoginConsentAsync() {
    ///lvfile/api/{app_name}/cloud/google/get-login-url
    //https://docker.lacviet.vn/lvfile/api/lv-docs/cloud/google/get-login-url
        var url = await api.post(`${this.appName}/cloud/google/get-login-url`, {

            scopes:[
                 "gmail.send","drive"
            ]

        });
        var windowName = "_blank";  // Name of the popup window
        var windowFeatures = "width=600,height=400";  // Size and other features (optional)

        window.open(url.Data, windowName, windowFeatures);

    }
    async doUpdateAndConsentAsync() {
        await this.doUpdateAsync();
        await this.getGoogleLoginConsentAsync();
    }
    async doUpdateAsync() {
        await api.post(`${this.appName}/cloud/google-settings/update`, {
            Token: window.token,
            ClientId: this.data.ClientId,
            ClientSecret: this.data.ClientSecret,
            Email: this.data.Email,
            AccessToken: this.data.AccessToken,
            RefreshToken: this.data.RefreshToken

        });

        this.$applyAsync();
    }
});
export default googleConfig;