import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var geminiServiceView = await View(import.meta, class SearchView extends BaseScope {
    async init() {
    var me=this;
    var mainEle = await this.$getElement();
    $(window).resize(()=>{
            $(mainEle).css({
                "max-height":$(document).height()-100
            })
        })
        $(mainEle).css({
                "max-height":$(document).height()-100
           })

    this.fileInput = mainEle.find("#file-input")[0];
    this.fileInput.addEventListener('change', (event) => {
          var  files = event.target.files;
          if (files.length > 0) {
                me.file=files[0];
                me.$applyAsync();
            }
    });
    this.dropzone = mainEle.find("#dropzone")[0];

    this.dropzone.addEventListener('dragover', (event) => {
          event.preventDefault(); // Prevent default browser behavior
          dropzone.classList.add('hover'); // Add hover effect
    });

    this.dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('hover'); // Remove hover effect
    });

    this.dropzone.addEventListener('drop', (event) => {
      event.preventDefault();
      dropzone.classList.remove('hover'); // Remove hover effect

      var files = event.dataTransfer.files; // Get dropped files

      if (files.length > 0) {
        me.file=files[0];
        me.$applyAsync();
      }
    });

        this.dropzone.addEventListener('click', () => {
            me.fileInput.click();
             // Trigger file selection dialog on click
        });

    }
    async doRunApIAsync(){

        alert(this.file)
    }
});
export default geminiServiceView;