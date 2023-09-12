import { ui_html } from "./ui_html.js";
import { ui_events } from "./ui_events.js";

import { ui_layouts } from "./ui_layouts.js";
class ui_component {
    ele;
    _width;
    _height;
    _flex;
    _eventHandle;
    constructor() {
        if (this.ele) {
            this._eventHandle = new ui_events.handler(this.ele);
        }
    }
    undraggable() {
        this.getEle().setAttribute("ondragstart", "return false;");
        this.getEle().setAttribute("ondrop", "return false;");
    }
    setEle(ele) {
        this.ele = ele;
        this.undraggable();
        this._eventHandle = new ui_events.handler(this.ele);
    }
    getEle() {
        return this.ele;
    }
    setContainer(ele) {
        if (ele instanceof ui_component) {
            ele.ele.appendChild(this.ele);
        }
        else {
            ele.appendChild(this.ele);
        }
    }
    layoutColumns() {
        ui_layouts.layoutColumns(this.ele);
    }
    layoutRows() {
        ui_layouts.layoutRows(this.ele);
    }
    dock() {
        var R = this.ele.getBoundingClientRect();
        this._width = R.width;
        this._height = R.height;
        this._flex = this.ele.style.flex;
        ui_layouts.dockFull(this.ele);
    }
    unDock() {
        ui_html.setStyle(this.ele, {
            flex: "unset",
            width: this._width.toString() + "px",
            height: this._height.toString() + "px"
        })
    }
    css(style) {
        ui_html.setStyle(this.ele, style);
    }
    setEvent(event) {
        this._eventHandle.set(event)
    }

}

class ui_container extends ui_component {

    constructor() {
        super();
        this.setEle(ui_html.createEle("div"));

    }
}

export { ui_component, ui_container} 