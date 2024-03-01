
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import {parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var fileInfoView = await View(import.meta, class FileInfoView extends BaseScope {
      async init() {


      }
      doAddNewTags(){
         if(!this.privileges){
            this.privileges=[{isNew:true}]
         }
         else {
            this.privileges.push({isNew:true})
         }
         this.$applyAsync();
      }
      doRemoveTags(tag){
            var ret=[];
            for(var i=0;i<this.privileges.length;i++){
                if (this.privileges[i]!=tag){
                    ret.push(this.privileges[i])
                }
            }
            this.privileges=ret;
            this.$applyAsync();

      }
      async doUpdateTags(){
            var privilegesData=[];
            this.privileges = this.privileges ||[]
            for(var i=0;i<this.privileges.length;i++){
                privilegesData.push({
                    Type:this.privileges[i].key,
                    Values:this.privileges[i].values
                })
            }

            this.data = await api.post(`${this.appName}/files/update_privileges`, {
                UploadIds: [this.uploadId],
                Data:privilegesData
            });
            this.$applyAsync();
      }
      async loadDetailInfo(appName, uploadId){
        this.appName=appName;
        this.uploadId=uploadId;
        this.data = await api.post(`${appName}/files/info`, {
            UploadId: uploadId
        });
        this.privileges =[];
        if (!this.data.ClientPrivileges){
            this.data.ClientPrivileges=[]
        }
        if (this.data.ClientPrivileges){

            for (var i=0;i<this.data.ClientPrivileges.length;i++){
                var keys=Object.keys(this.data.ClientPrivileges[i]);
                this.privileges.push({
                    key:keys[0],
                    values: this.data.ClientPrivileges[i][keys[0]]
                })
            }
        }

        this.$applyAsync();
      }
      async doCopy(){
      //{app_name}/files/clone
        this.ret= await api.post(`${this.appName}/files/clone`, {
            UploadId:this.uploadId
        });
      }
      async doSetMarkDelete(mark){
        this.ret= await api.post(`${this.appName}/files/mark_delete`, {
            UploadId:this.uploadId,
            IsDelete:mark
        });
      }


});
export default fileInfoView;