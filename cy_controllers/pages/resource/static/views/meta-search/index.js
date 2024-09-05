import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var searchViewMeta = await View(import.meta, class SearchView extends BaseScope {
   async loadMeta(item) {

        this.meta_data = JSON.stringify(item.meta_data, null, 2);
        this.$apply();
   }
});
export default searchViewMeta;