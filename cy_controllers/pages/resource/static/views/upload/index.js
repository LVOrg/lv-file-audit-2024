import { BaseScope, View } from "./../../js/ui/BaseScope.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError, msgOK } from "../../js/ui/core.js"

var uploadFileView = await View(import.meta, class UploadFileView extends BaseScope {
    debugger;
    appName = ""
    info = {}
    data = {
        tags:[],
        IsPublic:true
    }
    meta_text = JSON.stringify({})
    async init(){

    }
    setApp(appName) {

        if (!this.data){
            this.data={
                tags:[],
                IsPublic:true
            }
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
            alert(ex);
            return;
        }
        try {
            var reg = await api.post(`${this.appName}/files/register`, {
                Data: {
                    FileName: fileUpload.name,
                    FileSize: fileUpload.size,
                    ChunkSizeInKB: 1024 * 10,
                    IsPublic: this.data.IsPublic||false,
                    ThumbConstraints:"700,350,200,120",
                    Privileges: this.data.tags,
                    meta_data: meta_data
                }
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
                        msgError(chunk.Error.message)
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