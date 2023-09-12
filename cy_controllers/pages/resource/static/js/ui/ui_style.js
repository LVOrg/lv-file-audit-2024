import { ui_html } from "./ui_html.js";
class ui_style_css_block {
    selector;
    pSeudo;
    define;
    toString() {
        var ret = this._getName();
        ret = ret + this._defineToString();
        return ret;
    }
    _getName() {
        var ret = this.selector;
        for (var i = 0; i < this.pSeudo.length; i++) {
            if (this.pSeudo[i] && this.pSeudo[i] != "default") {
                ret += ":" + this.pSeudo[i];
            }
        }
        return ret;
    }
    _defineToString() {
        var me = this;
        var keys = Object.keys(this.define);
        var ret = "{";
        keys.forEach(k => {
            var key = me._getKey(k);
            ret += key + ":" + me.define[k] + ";";
        });

        return ret + "}";
    }
    _getKey(k) {
        var ret = "";
        for (var i = 0; i < k.length; i++) {
            var c = k[i];
            if (c == c.toUpperCase()) {
                ret += "-" + c.toLowerCase();
            }
            else {
                ret += c;
            }
        }
        return ret;
    }
};
class ui_style_builder {
    ele;
    blocks;
    constructor(name) {
        this.ele = ui_html.createEle("style");
        this.ele.setAttribute("name", name);
        this.blocks = {};
    }
    define(selector, css) {
        var _selector = selector;


        var block = this.blocks[_selector];
        if (!block) {
            this.blocks[_selector] = block = new ui_style_css_block();
            block.selector = _selector;
            block.pSeudo = [];

            block.define = css || {};
        }
        else {
            var keys = Object.keys(css || {});
            for (var i = 0; i < keys.length; i++) {
                block.define[keys[i]] = css[keys[i]];
            }
        }
        return block;
    }
    applyTo(ele) {

        var content = "";
        var me = this;
        var keys = Object.keys(this.blocks);
        keys.forEach(k => {
            var b = me.blocks[k];
            content += b.toString();
        });
        this.ele.innerHTML = content;
        ele.appendChild(this.ele);
    }
}
var ui_style = {
    cssBlock: ui_style_css_block,
    builder: ui_style_builder
};
export { ui_style }