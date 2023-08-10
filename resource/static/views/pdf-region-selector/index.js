import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_window } from "../js/ui/ui_window.js";
//import { ui_rect_picker } from "../js/ui/ui_rect_picker.js";
import { ui_pdf_desk } from "./../../js/ui/ui_pdf_desk.js";
import api from "./../../js/ClientApi/api.js"
import { redirect, urlWatching, getModule, dialogConfirm, newGuid } from "./../../js/ui/core.js"
/*import appEditView from "./app_edit/index.js"*/
console.log(dialogConfirm)
var pdfEditor = await View(import.meta, class PdfEditor extends BaseScope {
    list = []
    async init() {
        
        var ele = await this.$findEle("#edior");
        var regionMenu = await this.$findEle("#region-menu");
        this.editor = new ui_pdf_desk(ele[0]);
        this.editor.addToolbar($('<input type="button" value="Lưu"/>')[0],'save');
        console.log(this.editor.getToolbar());
        this.editor.setContextMenuOfSelectRegion(regionMenu[0])
        this.editor.onSelectPicker(async (region) => {
            

        });
        this.editor.onCtrlSelect(async (rect, ele, layer) => {
            debugger;
        });
        this.editor.onBeforeDeleteRegion(async () => {
            var isOK = await dialogConfirm("Bạn có muốn xóa vùng đang chọn hay không?");
            return !isOK;
        });
        this.editor.onBeforeBrowserFile(async () => {
            if (this.editor.getData().length > 0) {
                var isOK = await dialogConfirm("Thông tin đang biên tập có thể bị mất. Bạn có muốn lưu lại hay không?");
                return isOK;
            }
            
        });
        var fdpEditorEle = await this.$findEle('.pdf-picker-editor');
        fdpEditorEle.css({
            'max-height': $(window).height() - $('header').outerHeight() - 10,
            'min-width': $("#body").innerWidth()
        });
        this.editor.onLoadFileComplete(async (info) => {
            debugger;
            await this.editor.doLoadThumns(120, 100)
            fdpEditorEle.css({
                'max-height': $(window).height() - $('header').outerHeight() - 10,
                'min-width': $("#body").innerWidth()
            });
        });
        
        $(window).resize(() => {
            fdpEditorEle.css({
                'max-height': $(window).height() - $('header').outerHeight() - 10,
                'min-width': $("#body").innerWidth()
            });
        });

        //console.log(this.editor.editor);
        
    }
});

export default pdfEditor;