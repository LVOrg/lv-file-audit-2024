import { ui_html } from "./ui_html.js";
import { ui_editor_layers } from "./ui_editor_layers.js";
class ui_desk_region {
    start;
    end;

}
class ui_desk_page_of_picker {
    pageIndex
    pickers
}

class ui_desk_pdf_rect_picker_events {
    desk;
    constructor(desk) {
        this.desk = desk;
    }
    onContextMenu(cb) {
        this.desk._onContextMenu = cb;
    }
    onSelectPicker(cb) {
        this.desk._onSelectPicker = cb;
    }
    onAfterEdit(cb) {
        this.desk._onAfterEdit = cb;
    }
}
 class ui_desk_pdf_region_selection_meta {

}
class ui_desk_region_selection {
    x;
    y;
    widthr;
    height;
    meta
    constructor() {
        this.x = 0;
        this.y = 0;
        this.width = 0;
        this.height = 0;
    }
}
class ui_desk_pageRegion_selection {
    pageIndex;
    regions;
    constructor() {
        this.pageIndex = 0;
        this.regions = [];
    }
}
const ui_desk_desk_interact_emum = {
    resize : "resize",
    none : "none",
    draw : "draw",
    edit : "edit",
    scale : "scale"
}
class ui_desk_desk_interact {
    _owner;
    type;
    object;
    subObject;
    constructor(owner) {
        this._owner = owner;
    }
};
class ui_desk_desk_layers {
    desk;
    ele;
    layerBkgEle;
    drawLayer;
    dragLayer;
    resizeLayer;
    groupLayer;
    constructor(desk, ele) {

        this.desk = desk;
        this.ele = ele;
        var me = this;
        this.layerBkgEle = ui_html.createEle("div");
        this.ele.setAttribute("id", "desk-erea");
        this.desk.deskEle = ele;
        this.desk.canvas = ui_html.createEle("canvas");
        this.desk.ctx = this.desk.canvas.getContext("2d");
        this.desk.deskEle = ele;
        ui_html.setStyle(this.desk.deskEle, {
            position: "relative",
            overflow: "hidden",
            zIndex: "1"
        });
        ui_html.setStyle(this.desk.canvas, {
            position: "absolute",
            left: "0px",
            top: "0px"
        });
        this.ele.appendChild(this.layerBkgEle);
        this.layerBkgEle.appendChild(this.desk.canvas);
        ui_html.setStyle(this.layerBkgEle, {
            width: "100%",
            height: "100%",
            overflow: "auto",
            position: "absolute",
            left: "0px",
            top: "0px",
            float: "left"
        });
        var R = this.ele.getBoundingClientRect();
        ui_html.setStyle(this.layerBkgEle, {
            width: (R.width).toString() + "px",
            height: (R.height).toString() + "px",
            overflow: "auto"
        });
        this.drawLayer = new ui_editor_layers.rect(ele, this.layerBkgEle, evt => { return evt.keyCode == undefined && !evt.ctrlKey });
        this.drawLayer.setRectStyle({
            border: "dotted 2px #111"
        });
        this.dragLayer = new ui_editor_layers.dragger(ele, this.layerBkgEle);
        this.resizeLayer = new ui_editor_layers.resize(ele, this.layerBkgEle);
        this.zoomLayer = new ui_editor_layers.rect(ele, this.layerBkgEle, evt => {
            return evt.ctrlKey;

        });
    }

    applyDebugBorder(ele) {
        ui_html.setStyle(ele, {
            border: "solid 4px red",
            marginRight: "8px",
            marginBottom: "4px"
        });
    }
};
var ui_desk = {
    region: ui_desk_region,
    page_of_picker: ui_desk_page_of_picker,
    pdf_rect_picker_events: ui_desk_pdf_rect_picker_events,
    pdf_region_selection_meta: ui_desk_pdf_region_selection_meta,
    region_selection: ui_desk_region_selection,
    pageRegion_selection: ui_desk_pageRegion_selection,
    desk_interact_emum: ui_desk_desk_interact_emum,
    desk_interact: ui_desk_desk_interact,
    desk_layers: ui_desk_desk_layers

};
export { ui_desk };