import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var searchView = await View(import.meta, class LogsView extends BaseScope {


    async init() {

        this.data = await api.post(`logs/views`,{});
        this.listOfInstances = await api.post(`logs/list-instance`,{});
        this.listOfTypes = await api.post(`logs/list-types`,{});
        this.logLimit = 20;
        this.$applyAsync();
    }
    doLoadMore(sender) {
        var me=sender;

        api.post(`logs/views`,{
                FormTime: me.scope.logFrom,
                ToTime: me.scope.logTo,
                LogType: me.scope.logType,
                Instance: me.scope.logInstance,
                Limit: me.scope.logLimit,
                PageIndex: sender.pageIndex
        }).then(r => {
            sender.done(r);
        });


    }
    async doRefresh() {

        var me=this;

        this.data = await api.post(`logs/views`,{
                FormTime: me.logFrom,
                ToTime: me.logTo,
                LogType: me.logType,
                Instance: me.logInstance,
                Limit: me.logLimit
        })
        this.$applyAsync();
    }






});
export default searchView;