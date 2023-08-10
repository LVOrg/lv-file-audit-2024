import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var searchView = await View(import.meta, class LogsView extends BaseScope {


    async init() {

        this.data = await api.post(`logs/views`, {
            Token: window.token
        })


        this.$apply();
    }
    async doRefresh() {

        this.data = await api.post(`logs/views`, {
            Token: window.token
        })
        this.$applyAsync();
    }






});
export default searchView;