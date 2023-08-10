import { ui_component, ui_container } from "./ui_component.js";
import { ui_html } from "./ui_html.js";
import { ui_resource } from "./ui_resource.js";
import { ui_layouts } from "./ui_layouts.js";
//
class ui_toolbar_toolbarItem extends ui_container {
     _command;
    constructor() {
        super();
    }
    setCommand(command) {
        this._command = command;
        this.getEle().setAttribute("command", this._command);
        this.getEle().childNodes.forEach(p => {
            p.setAttribute("command", this._command)
        });
    }
    getCommand() {
        return this._command;
    }
}
class ui_toolbar_toolbarCommandItem extends ui_toolbar_toolbarItem {

    _img;
    constructor() {
        super();
        this._img = ui_html.createEle("img");
        this.getEle().appendChild(this._img);
    }
    setIconByBase64(base64) {
        this._img.setAttribute("src", ui_resource.urlFromImageBase64Text(base64));
    }


}
class ui_toolbar_toolbarInputItem extends ui_toolbar_toolbarItem {

    _input;
    _span;
    _afterSpan;
    constructor() {
        super();
        ui_layouts.layoutRows(this.getEle());
        this._span = ui_html.createEle("span");
        this._input = ui_html.createEle("input");
        this.getEle().appendChild(this._span);
        this.getEle().appendChild(this._input);
        this._afterSpan = ui_html.createEle("span");
        this.getEle().appendChild(this._afterSpan);
    }
    setAfteText(txt) {
        this._afterSpan.innerText = txt;
    }
    setText(txt) {
        this._span.innerText = txt;
    }
    getInput() {
        return this._input;
    }
}
class ui_toolbar_menuItem extends ui_toolbar_toolbarItem {

    _img;
    _span;
    constructor() {
        super();
        this._img = ui_html.createEle("img");
        this.layoutRows();
        this._span = ui_html.createEle("span");
        this.getEle().appendChild(this._img);
        this.getEle().appendChild(this._span);
    }
    setText(txt) {
        this._span.innerText = txt;
    }
}
class ui_toolbar_toolbar extends ui_container {
    items;
    _onCommand;
    constructor() {
        super();
        this.items = [];
        var me = this;
        this.setEvent({
            onclick: evt => {
                var target = evt.target;
                var command = target.getAttribute("command");
                if (command && command != null) {
                    if (me._onCommand) {
                        try {
                            me._onCommand(command);
                        } catch (e) {
                            console.error(e);
                        }
                    }
                }
            }
        });
    }

    onCommand(cb) {
        this._onCommand = cb;
    }
    add(item) {
        this.items.push(item);
        item.setContainer(this.getEle());

    }
    addByHtmlElement(ele, handler) {
        this.getEle().appendChild(ele);
        new q.events.handler(ele).set({
            onclick: evt => {
                handler();
            }
        });
    }
    replaceBy(ele) {
        this.getEle().innerHTML = "";
        //var child = ui_html.createEle("div");
        this.getEle().appendChild(ele);
        this.css({
            height: "unset",
            border: "unset",
            borderStyle: "none"
        });
        ui_html.setStyle(ele, {
            display: "flex"
        });
        //child.appendChild(ele);
    }
}
class ui_toolbar_h_toolBar extends ui_toolbar_toolbar {
    constructor() {
        super();
        this.layoutRows();
    }

}
class ui_toolbar_v_toolBar extends ui_toolbar_toolbar {
    constructor() {
        super();
        this.layoutColumns();
    }
}

var ui_toolbar = {
    toolbarItem: ui_toolbar_toolbarItem,
    toolbarCommandItem: ui_toolbar_toolbarCommandItem,
    toolbarInputItem: ui_toolbar_toolbarInputItem,
    menuItem: ui_toolbar_menuItem,
    toolbar: ui_toolbar_toolbar,
    h_toolBar: ui_toolbar_h_toolBar,
    v_toolBar: ui_toolbar_v_toolBar
}
export { ui_toolbar}