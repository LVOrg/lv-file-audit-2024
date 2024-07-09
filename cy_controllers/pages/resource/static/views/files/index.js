
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var filesView = await View(import.meta, class FilesView extends BaseScope {
    listOfApp = [undefined]
    appsMap = {}
    currentApp = undefined
    listOfFiles = []
    currentAppName = undefined
    hasSelected = false
    is_processing_error(item) {
        if (item.ProcessInfo) {
            if (item.ProcessInfo.content && item.ProcessInfo.content.IsError==true) {
                return true
            }
            if (item.ProcessInfo.image && item.ProcessInfo.image.IsError==true) {
                return true
            }
        }
        return false;
    }
    async init() {

        this.ui = {
            hasSelected: false
        }
        var queryData = parseUrlParams();
        var r = await this.$getElement();

        $(window).resize(() => {
            $(r).css({
                "max-height": $(document).height() - 100
            })
        })
        $(r).css({
            "max-height": $(document).height() - 100
        })


        this.listOfApp = await api.post(`admin/apps`, {

        })
        this.appsMap = {}
        for (var i = 0; i < this.listOfApp.length; i++) {
            this.appsMap[this.listOfApp[i].Name.toLowerCase()] = this.listOfApp[i];
        }
        this.currentApp = this.listOfApp[0];
        this.currentAppName = this.currentApp.Name;
        this.filterByDocType = "AllTypes"
        await this.doLoadAllFiles();
        this.$applyAsync();
        debugger;
    }
    async doEditAppFromFileExplorer(appName) {

        var r = await import("../app_edit/index.js");
        var app_edit = await r.default();
        await app_edit.doEditApp(appName);
        app_edit.asWindow();

    }
    async doLoadAllFileByApp(appName) {
        debugger;
        var indexOfApp = -1;

        while (indexOfApp < 0) {
            indexOfApp++;
            if (appName.toLowerCase() == this.listOfApp[indexOfApp].Name.toLowerCase()) {
                break;
            }
        }
        if ((indexOfApp >= 0) && (indexOfApp < this.listOfApp.length)) {
            this.currentApp = this.listOfApp[indexOfApp];
            this.currentAppName = this.currentApp.Name;
            this.listOfFiles = await api.post(`${appName}/files`, {

            });
            this.$applyAsync();
        }
    }
    async showAddTagsButton() {
        for (var i = 0; i < this.listOfFiles.length; i++) {
            if (this.listOfFiles[i].isSelected) {
                this.ui.hasSelected = true;
                this.$applyAsync();
                return;

            }
        }
        this.ui.hasSelected = false;
        this.$applyAsync();
    }
    async doAddTags() {
        this.showAddTags = true;
        this.$applyAsync();
    }
    async doLoadAllFiles() {
        debugger;
        ///lvfile/api/{app_name}/azure/get_login_url

        var me = this;
        if (this.appsMap[this.currentAppName.toLowerCase()]) {
            this.currentApp = this.appsMap[this.currentAppName.toLowerCase()];
            var azureLogin = await api.post(`${this.currentAppName}/azure/get_login_url`, {

            });
//            if (azureLogin.error) {
//                this.currentApp.AzureLoginUrl = undefined;
//            }
//            else {
//                this.currentApp.AzureLoginUrl = azureLogin.loginUrl;
//            }
//            console.log(this.currentApp)
            this.listOfFiles = await api.post(`${this.currentAppName}/files`, {
                DocType: me.filterByDocType,
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
    async showError(item) {
        var r = await import("../errors/index.js");
        var err = await r.default();
        err.setItem(item);
        err.asWindow();
    }
    async doShowWindowAddTags() {
        var r = await import("../tags-editor/index.js");
        var selectedId = []
        for (var i = 0; i < this.listOfFiles.length; i++) {
            if (this.listOfFiles[i].isSelected) {
                selectedId.push(this.listOfFiles[i].UploadId);

            }
        }
        var editor = await r.default();
        editor.setData(this.currentAppName, this, selectedId);
        editor.asWindow();
    }
    async doOpenUploadWindow(uploadId) {
        debugger;
        var uploadForm = await (await import("../upload/index.js")).default();
        uploadForm.setApp(this.currentAppName);
        uploadForm.setUploadId(uploadId);
        uploadForm.asWindow();
    }
    async doOpenUploadMultiFilesWindow() {
        debugger;

        var r = await import("../uploads/index.js");
        var viewer = await r.default();
        await viewer.setApp(this.currentAppName)
        var win = await viewer.asWindow();
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
            ValueSearch: sender.scope.fileNameSearchValue,
            DocType: sender.scope.filterByDocType,
        }).then(r => {
            sender.done(r);
        });

    }
    async doShowDetail(item) {

        var r = await import("../file-info/index.js");
        var viewer = await r.default();

        var win = await viewer.asWindow();
        win.doMaximize();
        await viewer.loadDetailInfo(this.currentAppName, item.UploadId)
        console.log(win);
    }
    async doReadableContent(item) {
        var r = await import("../content-info/index.js");
        var viewer = await r.default();
        await viewer.loadReadableContent(this.currentAppName, item.UploadId)
        var win = await viewer.asWindow();
        win.doMaximize()
    }
    async doLoadLayoutOCR(item) {
        var r = await import("../layout-ocr/index.js");
        var viewer = await r.default();
        var win = await viewer.asWindow();
        await viewer.loadLayoutOcrData(this.currentAppName, item.UploadId);
        win.doMaximize();

    }
    async doOpenWordInWindows(item) {
        var r = await import("../docx-view/index.js");
        var viewer = await r.default();
        var win = await viewer.asWindow();

        win.doMaximize();
        await viewer.loadWord(item);
    }
    clientOpenResource(tenant,
        resourceId,
        resourceExt,
        checkOutUrl,
        checkOutMethod,
        checkOutHeader,
        checkOutData,
        checkInUrl,
        checkInMethod,
        checkInHeader,
        checkInData,
        accessToken) {
        return new Promise((resolve, reject) => {
            try {
                var data = {
                    tenant: tenant,
                    resourceId: resourceId,
                    checkOutUrl: checkOutUrl,
                    checkOutMethod: checkOutMethod,
                    checkOutHeader: checkOutHeader,
                    checkOutData: checkOutData,
                    checkInUrl: checkInUrl,
                    checkInMethod: checkInMethod,
                    checkInHeader: checkInHeader,
                    checkInData: checkInData,
                    resourceExt: resourceExt,
                    accessToken: accessToken
                }
                var ws = new WebSocket("ws://127.0.0.1:8765");
                ws.onopen = () => {
                    ws.send(JSON.stringify(data));
                };
                ws.onmessage = function (event) {
                    var data = event.data; // Data received from the server
                    try {
                        var result = JSON.parse(event.data);
                        if (result.error_code) {
                            reject(result)
                        }
                        else {
                            resolve(result);
                        }
                    }
                    catch (error) {
                        reject(error)
                    }
                };
            } catch (error) {
                // If failed, call reject with the error
                reject(error);
            }
        });
    }
    async doEditInDesktopAppAsync(data) {

        return new Promise((resolve, reject) => {
            try {

                var ws = undefined
                try {
                    var ws = new WebSocket("ws://127.0.0.1:8765");
                }
                catch (ex) {
                    throw {
                        error_code: "AppNotInstall",
                        error_message: "Codx desktop application was not run or not install"
                    }
                }
                ws.onopen = () => {
                    ws.send(JSON.stringify(data));
                };
                ws.onmessage = function (event) {
                    var data = event.data; // Data received from the server
                    try {
                        var result = JSON.parse(event.data);
                        if (result.error_code) {
                            reject(result)
                        }
                        else {
                            resolve(result);
                        }
                    }
                    catch (error) {
                        reject(error)
                    }
                };
            } catch (error) {
                // If failed, call reject with the error
                reject(error);
            }
        });
    }
    async doEditInDesktop(item) {
        var me = this;
        var cookieString = document.cookie;
        var cookieName = "cy-files-token";
        var accessToken = cookieString.split("; ").find(cookie => cookie.startsWith(cookieName + "=")).split("=")[1];

        var url=$("head base").attr("href")
        var checkOutUrl = url + "api/files/check_out_source";
        var checkInUrl = url + "api/files/check_in_source";
        try {
            var items = item.FileName.split('.')
            var ext=""
            if (items.length > 1) {
                ext = items[items.length -1]
            }
            var ret = await me.doEditInDesktopAppAsync(
                {
                    resourceExt: ext,
                    src: {
                        url: checkOutUrl,
                        method: 'post',
                        header: {
                            "Authorization": "Bearer " + accessToken
                        },
                        data: {
                            appName: me.currentAppName,
                            uploadId: item.UploadId
                        }
                    },
                    dst: {
                        url: checkInUrl,
                        method: 'post',
                        header: {
                            "Authorization": "Bearer " + accessToken
                        },
                        data: {
                            appName: me.currentAppName,
                            uploadId: item.UploadId
                        }
                    }
                }
            )
        }
        catch (error) {
            msgError(error);
        }

    }
    async doLoadGeminiAssistantWindow(item) {
            var r = await import("../gemini-assistant/index.js");
            var geminiAssistant = await r.default();
            geminiAssistant.setInfo(this.currentAppName,item,this);
            var win = await geminiAssistant.asWindow();
            win.doMaximize();
    }
    async doLoadCloudGoogleConfigAsync(){
        var me=this;
        var r = await import("../cloud-config-google/index.js");
            var cloudConfigGoogle = await r.default();
            await cloudConfigGoogle.setInfoAsync(this.currentAppName);
            var win = await cloudConfigGoogle.asWindow();
            win.doMaximize();
    }
});
export default filesView;