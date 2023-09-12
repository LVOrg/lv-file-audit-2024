import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import {parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var docxViewerView = await View(import.meta, class FilesView extends BaseScope {
    dataItem = undefined
    async loadWord(item){
        this.dataItem=item;
        var me=this;
        var viewer= await me.$findEle("#viewer");
        var frm=$('<iframe id="viewer" height="100%" width="100%" srcdoc="<div></div>"></iframe>')[0]
        $(frm).appendTo(viewer[0]);
            var response = await fetch(item.UrlOfServerPath);
            var blob =await response.blob();

                //var divView=$("<div style='border:solid 4px red'></div>");

                //divView.appendTo(frmContent[0]);
                //var docData = item.UrlOfServerPath;
                var fx=0;
                fx=setInterval(()=>{
                    var frmContent=$(frm).contents().find('body');
                    console.log(frmContent)
                    var scriptTag = "<script src='static/js/vendors/docx-view/polyfill.min.js'></script>";
                    frmContent.append(scriptTag);
                    var script2Tag = "<script src='static/js/vendors/docx-view/jszip.min.js'></script>";
                    frmContent.append(scriptTag);
                    var script3Tag = "<script src='static/js/vendors/docx-view/docx-preview.min.js'></script>";
                    frmContent.append(script3Tag);
            /*
             <script src="static/js/vendors/docx-view/polyfill.min.js"></script>
<!--lib uses jszip-->
<script src="static/js/vendors/docx-view/jszip.min.js"></script>
<script src="static/js/vendors/docx-view/docx-preview.min.js"></script>
            */
                    docx.renderAsync(blob, frmContent.find('div')[0]).then(()=>{
                        clearInterval(fx);
                    });

                },200);



//        fetch(item.UrlOfServerPath)
//          .then(response => response.blob())
//          .then(blob => {
//                var frmContent=viewer.contents().find('body');
//                var divView=$("<div></div>");
//                divView.appendTo(frmContent);
//                var docData = item.UrlOfServerPath;
//                docx.renderAsync(blob, divView[0]).then(()=>{
//                });
//
//          });


    }
});
export default docxViewerView;