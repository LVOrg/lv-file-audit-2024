import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var searchView = await View(import.meta, class SearchView extends BaseScope {
    listOfApp = [1]
    currentApp = undefined
    listOfFiles = []
    highlight=false
    currentAppName = undefined
    SearchExpr = "conent search '... your content here...'"
    async init() {
        var mainEle = await this.$getElement();
        $(window).resize(()=>{
                $(mainEle).css({
                    "max-height":$(document).height()-100
                })
            })
            $(mainEle).css({
                    "max-height":$(document).height()-100
               })
        this.listOfApp = await api.post(`admin/apps`, {
            Token: window.token
        })
        this.currentApp = this.listOfApp[0];
        this.currentAppName = this.currentApp.Name;
        this.highlight = false;
        this.searchContent="((((meta_info.FolderPath like 'Quản lý công văn\\Công văn đến')) and (privileges['1']  like ['u-lv110'])) and (meta_info.FileName like 'Hợp đồng.pdf')) and (content like 'cong hoa xa hoi chu nghia')"
        
        this.$apply();
        await this.doFullTextSearch();
    }
    doSearchMore(sender) {

        if(sender.scope.highlight){
            api.post(`${sender.scope.currentAppName}/search`, {
                content: sender.scope.searchContent,
                page_size:sender.pageSize,
                page_index:sender.pageIndex,
                highlight:sender.scope.highlight,
                filter: sender.scope.SearchExpr
            }).then(r=>{
               sender.done(r.items);
            });
        }
        else {
            sender.data = api.post(`${sender.scope.currentAppName}/search`, {
                content: sender.scope.searchContent,
                page_size:sender.pageSize,
                page_index:sender.pageIndex,
                filter: sender.scope.SearchExpr
            }).then(r=>{
               sender.done(r.items);
            });
        }

    }
    async doFullTextSearch(page_index,sender) {
        page_index= page_index||0
       if(this.highlight){
            this.data = await api.post(`${this.currentAppName}/search`, {
                content: this.searchContent,
                page_size:20,
                page_index:page_index,
                highlight:this.highlight,
                filter: this.SearchExpr
            });
            this.$applyAsync();
        }
        else {
            this.data = await api.post(`${this.currentAppName}/search`, {
                content: this.searchContent,
                page_size:20,
                page_index:page_index,
                filter: this.SearchExpr
            });
            this.$applyAsync();
        }
    }
    
    async doOpenWordInWindows(item) {
        var r = await import("../docx-view/index.js");
        var viewer = await r.default();
        var win =await viewer.asWindow();

        win.doMaximize();
        await viewer.loadWord(item);
    }
    async doShowCodxMeta(item) {
        var r = await import("../meta-search/index.js");
        var metaViewer = await r.default();
        var win =await metaViewer.asWindow();

        win.doMaximize();
        await metaViewer.loadMetaFromAPIAsync(this.currentAppName,item);
    }
    async doReadableContent(item) {
        var r = await import("../content-info/index.js");
        var viewer = await r.default();
        await viewer.loadReadableContent(this.currentAppName, item.UploadId||item._id)
        var win = await viewer.asWindow();
        win.doMaximize()
    }
    
   
});
export default searchView;