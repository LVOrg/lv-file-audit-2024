
import { BaseScope, View } from "./../js/ui/BaseScope.js";
import { ui_window } from "../js/ui/ui_window.js";
import { ui_rect_picker } from "../js/ui/ui_rect_picker.js";
import { ui_pdf_desk } from "../js/ui/ui_pdf_desk.js";
import api from "../js/ClientApi/api.js"
import { redirect, urlWatching, getModule } from "../js/ui/core.js"
/*import appEditView from "./app_edit/index.js"*/
var homeView = await View(import.meta, class homeview extends BaseScope {
    list = []
    onInit(){
        //        this.loadData("hps-file-test").then();
        
        
    }
    doRedirect(subPage) {
        redirect(subPage);
    }
    async start() {
        var me = this;
       
    }
    async doEdit(appName) {
        redirect("edit/" + appName)
    }
    async doNew() {
        redirect("register")
    }
    async browserAllFiles() {
        redirect("files")
    }
    async getListOfApps() {
        debugger;
        this.list = await api.post("admin/apps", {
            Token: window.token
        });
        this.$applyAsync();
        
    }
    async loadFullTextSearch() {
        redirect("search")
    }
    async init() {
        await getListOfApps();
    } 
});

export default homeView;