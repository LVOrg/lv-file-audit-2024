
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import {parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var filesView = await View(import.meta, class FilesView extends BaseScope {
    listOfApp = [undefined]
    appsMap = {}
    currentApp = undefined
    listOfFiles = []
    currentAppName = undefined
    hasSelected=false
    async init() {
        this.ui={
            hasSelected:false
        }
        var queryData = parseUrlParams();
        var r =await this.$getElement();
        $(window).resize(()=>{
                $(r).css({
                    "max-height":$(document).height()-100
                })
            })
            $(r).css({
                    "max-height":$(document).height()-100
                })


        this.listOfApp = await api.post(`admin/apps`, {
            
        })
        this.appsMap={}
        for(var i=0;i<this.listOfApp.length;i++){
            this.appsMap[this.listOfApp[i].Name.toLowerCase()]=this.listOfApp[i];
        }
        this.currentApp = this.listOfApp[0];
        this.currentAppName = this.currentApp.Name;
        await this.doLoadAllFiles();
        this.$applyAsync();
        debugger;
    }
    async doEditApp(appName) {

          var r = await import("../app_edit/index.js");
            var app_edit = await r.default();
            await app_edit.doEditApp(appName);
            app_edit.asWindow();

    }
    async doLoadAllFileByApp(appName) {
        debugger;
        var indexOfApp=-1;

        while(indexOfApp<0) {
            indexOfApp++;
            if(appName.toLowerCase()==this.listOfApp[indexOfApp].Name.toLowerCase()) {
                break;
            }
        }
        if((indexOfApp>=0)&&(indexOfApp<this.listOfApp.length)) {
            this.currentApp = this.listOfApp[indexOfApp];
            this.currentAppName = this.currentApp.Name;
            this.listOfFiles = await api.post(`${appName}/files`, {

            });
            this.$applyAsync();
        }
    }
    async showAddTagsButton(){
        for(var i=0;i<this.listOfFiles.length;i++){
            if(this.listOfFiles[i].isSelected){
                this.ui.hasSelected=true;
                this.$applyAsync();
                return;

            }
        }
        this.ui.hasSelected=false;
        this.$applyAsync();
    }
    async doAddTags(){
        this.showAddTags= true;
        this.$applyAsync();
    }
    async doLoadAllFiles() {
        debugger;
        var me = this;
            if(this.appsMap[this.currentAppName.toLowerCase()]) {
                this.currentApp = this.appsMap[this.currentAppName.toLowerCase()];
                console.log(this.currentApp )
                this.listOfFiles = await api.post(`${this.currentAppName}/files`, {

                PageIndex: 0,
                PageSize: 20,
                FieldSearch: "FileName",
                ValueSearch: me.fileNameSearchValue
                });
                this.$applyAsync();
            }

    }

    async doSearchByFileName() {
        await this.doLoadAllFiles();
    }
    async doOpenInWindows(item) {
        var r = await import("../player/index.js");
        var player = await r.default();
        player.playByItem(item);
        player.asWindow();



    }
    async doShowWindowAddTags() {
        var r = await import("../tags-editor/index.js");
        var selectedId=[]
        for(var i=0;i<this.listOfFiles.length;i++){
            if(this.listOfFiles[i].isSelected){
                selectedId.push(this.listOfFiles[i].UploadId);

            }
        }
        var editor = await r.default();
        editor.setData(this.currentAppName, this,selectedId);
        editor.asWindow();
    }
    async doOpenUploadWindow() {
        debugger;
        var uploadForm = await (await import("../upload/index.js")).default();
        uploadForm.setApp(this.currentAppName);
        uploadForm.asWindow();
    }
    async doOpenUploadMultiFilesWindow() {
        debugger;

        var r = await import("../uploads/index.js");
        var viewer = await r.default();
        await viewer.setApp(this.currentAppName)
         var win =await viewer.asWindow();
         win.doMaximize()
    }
    async doOpenUploadZipWindow() {
        var uploadZipForm = await (await import("../zip_upload/index.js")).default();
        uploadZipForm.setApp(this.currentAppName);
        uploadZipForm.asWindow();
    }
    async doDelete(item) {
        if (await dialogConfirm(this.$res("Do you want to delete this item?"))) {
            var reg = await api.post(`${this.currentAppName}/files/delete`, {
                UploadId: item.UploadId
            });
            var ele = await this.$findEle(`[file-id='${item.UploadId}']`);
            ele.remove();
        }
    }
    doLoadMore(sender) {

        api.post(`${sender.scope.currentAppName}/files`, {
            Token: window.token,
            PageIndex: sender.pageIndex,
            PageSize: sender.pageSize,
            FieldSearch: "FileName",
            ValueSearch: sender.scope.fileNameSearchValue
        }).then(r => {
            sender.done(r);
        });

    }
    async doShowDetail(item){

        var r = await import("../file-info/index.js");
        var viewer = await r.default();
        await viewer.loadDetailInfo(this.currentAppName,item.UploadId)
         var win =await viewer.asWindow();
         win.doMaximize()
         console.log(win);
    }
    async doReadableContent(item){
        var r = await import("../content-info/index.js");
        var viewer = await r.default();
        await viewer.loadReadableContent(this.currentAppName,item.UploadId)
         var win =await viewer.asWindow();
         win.doMaximize()
    }
    async doLoadLayoutOCR(item) {
        var r = await import("../layout-ocr/index.js");
        var viewer = await r.default();
        var win =await viewer.asWindow();
        await viewer.loadLayoutOcrData(this.currentAppName,item.UploadId);
        win.doMaximize();

    }
    async doOpenWordInWindows(item) {
        var r = await import("../docx-view/index.js");
        var viewer = await r.default();
        var win =await viewer.asWindow();

        win.doMaximize();
        await viewer.loadWord(item);
    }
});
export default filesView;