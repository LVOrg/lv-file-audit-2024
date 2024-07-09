import { BaseScope, View } from "./../../js/ui/BaseScope.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError, msgOK } from "../../js/ui/core.js"

var uploadFileView = await View(import.meta, class UploadFileView extends BaseScope {
    debugger;
    appName = "";
    info = {};
    uploadId = undefined;
    data = {
        tags:[],
        IsPublic:true,
        storageType:"local",
        onedriveScope:"anonymous"
    };
    uploadConfig= {
        chunkSize:1024*10
    };
    meta_text = JSON.stringify({});
    Options = {};
    async init(){

    }
    setUploadId(uploadId) {
        this.uploadId=uploadId;
    }
    setApp(appName) {

        if (!this.data){
            this.data={
                tags:[],
                IsPublic:true,
                storageType:"local",
                onedriveScope:"anonymous"
            };
        }
        if(!this.uploadConfig) {
            this.uploadConfig = {
                chunkSize:1024*10
            };
        }
        this.appName = appName;
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
    async doUploadFile() {
        debugger;

        var me=this;
        var delay=(t)=>{
            return new Promise((r,x)=>{
                setTimeout(()=>{
                    r()
                },t);
            })
        };
        var file = this.$elements.find("#file")[0];
        if (file.files.length == 0) {
            msgError(this.$res("Please select file"));
            return;
        }
        var fileUpload = file.files[0];
        var meta_data = {}
        try {
            this.meta_text = this.meta_text|| '{}'
            meta_data = eval("()=>{ return "+this.meta_text+"}")()

        }
        catch (ex) {
            msgError(ex);
            return;
        }
        try {
            debugger;
            var reg = await api.post(`${this.appName}/files/register`, {
                Data: {
                    UploadId: this.uploadId,
                    FileName: fileUpload.name,
                    FileSize: fileUpload.size,
                    ChunkSizeInKB: me.uploadConfig.chunkSize,
                    IsPublic: this.data.IsPublic||false,
                    ThumbConstraints:"700,350,200,120",
                    Privileges: this.data.tags,
                    meta_data: meta_data,
                    storageType: this.data.storageType,
                    onedriveScope: this.data.onedriveScope,
                    onedriveExpiration: this.data.onedriveExpiration,
                    encryptContent: true,
                    googlePath: this.data.googlePath
                },
                SkipOptions: this.Options
            });
            if (reg.Error) {
                msgError(reg.Error.Message)
                return
            }
            else {
                this.info = reg.Data;
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
                    }, true);
                    await delay(10)
                    if (chunk.Error) {
                        msgError(chunk.Error.message||chunk.Error.Message)
                        return
                    }
                    this.info = chunk.Data;
                    this.$applyAsync();
                }
                msgOK(this.$res("Uploading was complete"));
            }
            
            
        }
        catch (ex) {
            alert(ex);
        }
        
    }
});
export default uploadFileView;