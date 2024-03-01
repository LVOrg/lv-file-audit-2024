import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import {parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var geminiAssistantView = await View(import.meta, class FilesView extends BaseScope {
    dataItem = undefined;

    setInfo(appName,item,parent) {
        this.appName=appName;
        this.doc =item;
        this.$applyAsync();
        this.parent=parent;
        this.data= {
            question:undefined,
            result:undefined

        };

    }
    async doPredictAsync(){
      this.data.result= await api.post(`${this.appName}/files/gemini-assistant`, {
            UploadId:this.doc.UploadId,
            Question:this.data.question
        });
       this.$applyAsync();
    }
    async doInspectContentAsync(){
            var r = await import("../inspect-content/index.js");
            var inspectContent = await r.default();
            await inspectContent.inspectAsync(this.appName,this.doc,this);
            var win = await inspectContent.asWindow();
            win.doMaximize();
    }
});
export default geminiAssistantView;