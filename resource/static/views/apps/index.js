import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"
/*import appEditView from "./app_edit/index.js"*/
var appsView = await View(import.meta, class AppsView extends BaseScope {
    list = [{}]
    
    async init() {
        await this.getListOfApps();
    }
    

    //async start() {
    //    var me = this;

    //}
    async doEdit(appName) {
        redirect("register?app=" + appName)
    }
    async doNew() {
        redirect("register")
    }
    //async browserAllFiles() {
    //    redirect("files")
    //}
    async getListOfApps() {
        debugger;
        this.listOfApps = await api.post("admin/apps", {
           
        });
        this.$applyAsync();

    }
    //async loadFullTextSearch() {
    //    redirect("search")
    //}

});

export default appsView;