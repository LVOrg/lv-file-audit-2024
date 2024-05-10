
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


        this.listOfApp = await api.post(`admin/apps`, {

        })
        this.appsMap = {}
        for (var i = 0; i < this.listOfApp.length; i++) {
            this.appsMap[this.listOfApp[i].Name.toLowerCase()] = this.listOfApp[i];
        }
        this.currentApp = this.listOfApp[0];
        this.currentAppName = this.currentApp.Name;
        this.filterByDocType = "AllTypes"
        await this.doLoadAllFiles();
        this.$applyAsync();
        debugger;
    }

});
export default googleConfig;