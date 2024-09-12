import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var searchViewMeta = await View(import.meta, class SearchView extends BaseScope {
   async loadMeta(item) {

        this.meta_data = JSON.stringify(item.meta_data, null, 2);
        this.$applyAsync();
   }
   async loadMetaFromAPIAsync(appName,item) {
        //
        this.appName=appName;
        this.uploadId=item.UploadID || item._id;
        var txtJSON  = await api.post(`${this.appName}/meta_info/get`, {
                UploadId: this.uploadId
            });
        this.meta_data =  JSON.stringify(txtJSON, null, 4);
        this.$applyAsync();
   }
   async doUpdateMetaAsync() {
        debugger;
        var me=this;
        var txt = await this.$findEle("textarea");
        console.log(txt);

        var updateMeta = null
        try
        {
            updateMeta= JSON.parse(txt.val())
            alert(updateMeta);

                 await api.post(`${me.appName}/meta_info/save`, {
                  "UploadId": me.uploadId,
                  "meta": updateMeta
                  });
        }
        catch (e){
            alert(e)
        }

   }
});
export default searchViewMeta;