import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import {parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var inspectContentView = await View(import.meta, class FilesView extends BaseScope {
    dataItem = undefined;

    async inspectAsync(appName,item,parent) {
        this.appName=appName;
        this.doc =item;
        this.$applyAsync();
        this.parent=parent;
        var res = await api.post(`${this.appName}/files/inspect-content`, {
            UploadId:this.doc.UploadId
        });

        if (res.error) {
            alert(res.error.description);
        }
        else {

            this.content=res.content;
            this.$applyAsync();
        }

    }
});
export default inspectContentView;