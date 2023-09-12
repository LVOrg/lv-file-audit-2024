
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import {parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var tagEditor = await View(import.meta, class TagEditor extends BaseScope {
    uploadIds=[]
    setData(appName, owner, data) {
        this.appName=appName;
        this.uploadIds=data;
        this.owner=owner;
        console.log(this.uploadIds);
    }
    doDeleteTag(item){
        var ret=[];
        for(var i=0;i<this.owner.tags.length;i++){
            if(this.owner.tags[i]!=item){
                ret.push(this.owner.tags[i]);
            }
        }
        this.owner.tags=ret;
        this.$applyAsync();
    }
    doAddTag() {
        if(!this.owner.tags){
            this.owner.tags=[{}];
        }
        else {
            this.owner.tags.push({});
        }
        this.$applyAsync();
    }
    async doPostAddTags(){
        var privilegesData=[];
            this.privileges = this.owner.tags ||[]
            for(var i=0;i<this.privileges.length;i++){
                privilegesData.push({
                    Type:this.privileges[i].key,
                    Values:this.privileges[i].values
                })
            }

            this.data = await api.post(`${this.appName}/files/add_privileges`, {
                UploadIds: this.uploadIds,
                Data:privilegesData
            });
            this.$applyAsync();
    }
    async doPostRemoveTags() {
        var privilegesData=[];
            this.privileges = this.owner.tags ||[]
            for(var i=0;i<this.privileges.length;i++){
                privilegesData.push({
                    Type:this.privileges[i].key,
                    Values:this.privileges[i].values
                })
            }

            this.data = await api.post(`${this.appName}/files/remove_privileges`, {
                UploadIds: this.uploadIds,
                Data:privilegesData
            });
            this.$applyAsync();
    }
});
export default tagEditor;