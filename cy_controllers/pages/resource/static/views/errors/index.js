import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"
/*import appEditView from "./app_edit/index.js"*/
var errorView = await View(import.meta, class AppsView extends BaseScope {
    setItem(item) {
        this.item=item;
        this.txt=JSON.stringify(item.ProcessInfo, null, 4); // Indent with 4 spaces
        this.$applyAsync();
    }
});
export default errorView;