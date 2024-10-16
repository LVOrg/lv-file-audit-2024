import { BaseScope, View } from "./../../js/ui/BaseScope.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError, msgOK } from "../../js/ui/core.js"

var uploadFilesView = await View(import.meta, class UploadFileView extends BaseScope {
    debugger;
    appName = ""
    info = {}
    data = {
        tags:[],
        IsPublic:true,
        ChunkSizeInKB: 1024 * 10
    }
    ChunkSizeInKB = 1024 * 10
    meta_text = JSON.stringify({})
    async init(){
        debugger;
        this.ChunkSizeInKB = 1024 * 10;
        this.applyAsync();
    }
    setApp(appName) {

        if (!this.data){
            this.data={
                tags:[],
                IsPublic:true
            }
        }
        this.appName = appName;
        this.info = {}
        this.ChunkSizeInKB = 1024 * 10;
        this.$applyAsync();
    }
    doAddTag(){
        if (!this.data){
            this.data={
                tags:[],
                IsPublic:true
            }
        }
        this.data.tags.push({});
        this.$applyAsync();
    }
    async uploadOneFile(fileUpload){
        var me=this;


        try {
            debugger;
            var reg = await api.post(`${this.appName}/files/register`, {
                Data: {
                    FileName: fileUpload.name,
                    FileSize: fileUpload.size,
                    ChunkSizeInKB: me.ChunkSizeInKB,
                    IsPublic: this.data.IsPublic||false,
                    ThumbConstraints:"700,350,200,120",
                    Privileges: this.data.tags,
                    meta_data: {}
                }
            },true);
            if (reg.Error) {
                msgError(reg.Error.Message)
                return
            }
            else {
                this.info[fileUpload.name] = {
                    "info":reg.Data,
                    "name":fileUpload.name
                } ;
                this.$applyAsync();
                var regData = reg.Data;
                debugger;
                for (var i = 0; i < regData.NumOfChunks; i++) {
                    var start = i * regData.ChunkSizeInBytes;
                    var end = Math.min((i + 1) * regData.ChunkSizeInBytes, fileUpload.size);
                    var filePartBlog = fileUpload.slice(start, end)
                    var filePart = new File([filePartBlog], fileUpload.name);
                    var chunk = await api.formPost(`${this.appName}/files/upload`, {
                        UploadId: regData.UploadId,
                        Index: i,
                        FilePart: filePart
                    },true);

                    if (chunk.Error) {
                        msgError(chunk.Error.message)
                        return
                    }
                    this.info[fileUpload.name]["chunk_info"] = chunk.Data;
                    this.$applyAsync();
                }
                msgOK(this.$res("Uploading was complete"));
            }


        }
        catch (ex) {
            msgError(ex);
        }
    }
    async doUploadFiles() {
        debugger;
        var actions = []
        var me=this;
        var file = this.$elements.find("#file")[0];
        if (file.files.length == 0) {
            msgError(this.$res("Please select file"));
            return;
        }
        var fileUploads = file.files;
        for(var i=0;i<fileUploads.length;i++) {
            actions.push(me.uploadOneFile(fileUploads[i]))

        }

        await Promise.all(actions);
        msgOK(this.$res("All files were uploaded"));

        
    }
});
export default uploadFilesView;