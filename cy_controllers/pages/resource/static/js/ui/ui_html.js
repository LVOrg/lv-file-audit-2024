import { ui_linear } from "./ui_linear.js";
class ui_Shape {
    canvas;
    ctx;
    startDrag;
    owner;
    desk;
    scaleSize = 1;
    x;
    y;
    w;
    h;
    name;
    constructor() {

        this.canvas = ui_html.createEle("canvas");
        this.ctx = this.canvas.getContext("2d");

        this.listener = [];

    }
    raiseEvent(name, evt) {
        for (var i = 0; i < this.listener.length; i++) {
            if (this.listener[i].name.indexOf(name) > -1) {
                this.listener[i].handler(evt);
            }
        }
    }

    loadTo(ele) {
        ele.appendChild(this.canvas);
        this.owner = ele;

    }
    listener = [];
    attachEvent(event) {
        var found = false;
        for (var i = 0; i < this.listener.length; i++) {
            found = this.listener[i] == event;
            if (found) {
                break;
            }
        }
        if (!found) {
            this.listener.push(event);
            var name = event.name.split(',')
            for (var i = 0; i < name.length; i++) {
                if (this.canvas[name[i]] == null ||
                    this.canvas[name[i]] == undefined) {
                    var fh = new eventHandle(name[i], event.handler);
                    this.canvas[name[i]] = (evt) => {

                        this.raiseEvent(fh.name, evt);
                    }
                }
            }
        }
    };
    removeEvent(event) {
        var newList = [];
        for (var i = 0; i < this.listener.length; i++) {
            if (this.listener[i] != event) {
                newList.push(this.listener[i]);

            }
        }
        this.listener = newList;
    }
    draw() {
        this.ctx.fillStyle = "#FF0000";
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
}
var ui_html = {
    HANDLE_SIZE: 10,
    getClientCoordinate: function (evt, owner) {
        if (owner) {
            return new ui_linear.vector(evt.clientX + owner.scrollLeft, evt.clientY + owner.scrollTop);
        }
        else {
            return new ui_linear.vector(evt.clientX , evt.clientY);
        }
    },
    eventHandle: class {
        name;
        handle;
        constructor(name, handle) {
            this.name = name;
            this.handle = handle;
        }
    },
    eventInfo: class {
        name;
        handler;
        constructor(
            owner,
            name, handler) {
            this.name = name;
            this.handler = handler;
        }
    },
    Shape: ui_Shape ,
    Rect: class Rect extends ui_Shape {
        constructor(x, y, w, h) {
            super();
            this.x = Math.ceil(x);
            this.y = Math.ceil(y);
            this.w = Math.ceil(w);
            this.h = Math.ceil(h);
            ui_html.setStyle(this.canvas, {
                position: "absolute",
                left: this.x.toString() + "px",
                top: this.y.toString() + "px",
                width: this.w.toString() + "px",
                height: this.h.toString() + "px"
            })

            this.canvas.width = this.w;
            this.canvas.height = this.h;
            this.draw();
        }
        draw() {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.beginPath();
            this.ctx.rect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.stroke();
            this.ctx.closePath();
        }
        sizeTo(w, h) {
            this.w = Math.ceil(w);
            this.h = Math.ceil(h);
            ui_html.setStyle(this.canvas, {
                width: this.w.toString() + "px",
                height: this.h.toString() + "px"
            })

            this.canvas.width = this.w;
            this.canvas.height = this.h;
            this.draw();
        }
    },
    pickerHandle: class {
        draw(ctx) {
            ctx.fillRect(this.x, this.y, this.w, this.h);
        }

        x;
        y;
        w;
        h;
        cursor;
        constructor(size) {
            this.w = size;
            this.h = size
        }
    },

    DOMRectObserve: class {
        ele;
        rect;
        _onChange;
        constructor(ele) {
            this.ele = ele;
            this.rect = this.ele.getBoundingClientRect();
            this._run();
        }
        onChange(cb) {
            this._onChange.push(cb);
        }
        _run() {
            var me = this;
            function r() {
                var rect = me.ele.getBoundingClientRect();
                if (rect.left != me.rect.left ||
                    rect.top != me.rect.top ||
                    rect.width != me.rect.width ||
                    rect.height != me.rect.height) {
                    me._onChange.forEach(f => {
                        f(rect);
                    });
                    me.rect = rect;
                }
                setInterval(() => {
                    r();
                }, 100);
            }
            r();



        }
    },
    UIDOMReady: class {
        ele;
        _cb
        constructor(ele, cb) {
            this.ele = ele;
            this._cb = cb;
            this._run();
        }
        _run() {
            var me = this;
            function R() {
                var r = window.getComputedStyle(me.ele);
                if (r.display != "") {
                    me._cb(me.ele.getBoundingClientRect());
                }
                else {
                    setTimeout(R, 10);
                }
            }
            R();
        }
    },
    getIndexInParent: function (ele) {
        var pNode = ele.parentNode.childNodes;
        var keys = Object.keys(pNode);
        for (var i = 0; i < keys.length; i++) {
            if (pNode[keys[i]] == ele) {
                return Number(keys[i]);
            }
        }
    },
    createEle: function (tag, style) {
        var ret = window.document.createElement(tag.toLocaleUpperCase());
        if (style) {
            var keys = Object.keys(style);
            keys.forEach((k, i) => {
                if (style[k] && style[k] != null) {
                    ret.style[k] = style[k];
                }
            });
        }
        return ret;
    },
    createInput: function (type, style) {
        var ret = window.document.createElement("INPUT");
        ret.setAttribute("type", type);
        if (style) {
            var keys = Object.keys(style);
            keys.forEach((k, i) => {
                if (style[k] && style[k] != null) {
                    ret.style[k] = style[k];
                }
            });
        }
        return ret;
    },
    setStyle: function (ele, style) {
        if (ele && ele.style) {
            if (style) {
                var keys = Object.keys(style);
                keys.forEach((k, i) => {
                    if (style[k] && style[k] != null) {
                        ele.style[k] = style[k];
                    }
                });
            }
        }

    },
    setAttrs: function (ele, style) {
        if (style) {
            var keys = Object.keys(style);
            keys.forEach((k, i) => {
                if (style[k] && style[k] != null) {
                    ele.setAttribute(k, style[k]);
                }
            });
        }
    },
    unselectable: function (ele, style) {

        ui_html.setStyle(ele, {
            userSelect: "none",
            webkitUserSelect: "none",
        });
        ui_html.setAttrs(ele, {
            onselectstart: "return false;",
            onmousedown: "return false;"
        });
    },
    iframeCreate: function (ownerEle, onReady) {
        return new Promise(function (resolve, reject) {
            var iframe = createEle("iframe", {
                width: "100%",
                height: "100%",
                float: "left"
            });
            iframe.setAttribute("frameBorder", "0");
            iframe.onload = (evt) => {

                resolve(iframe);
            }
            ownerEle.appendChild(iframe);
        });


    },
    canvasCreate: function (ownerEle) {

        var canvas = ui_html.createEle("canvas")
        var R = ownerEle.getBoundingClientRect();
        var W = Math.ceil(R.width);
        var H = Math.ceil(R.height);
        ui_html.setStyle(canvas, {
            width: W.toString() + "px",
            height: H.toString() + "px"
        })

        canvas.width = W;
        canvas.height = H;
        ownerEle.appendChild(canvas);
        return canvas;
    },
    showEleInContainerWithPosMouseEventPosition: function (container, ele, evt) {
        var pos = getClientCoordinate(evt, container);
        ele.style.position = "absolute";
        
        ele.style.left = pos.x.toString() + "px";
        ele.style.top = pos.y.toString() + "px";
        ele.style.display = "block";

        container.appendChild(ele);

    },
    getLeftTopOfEle: function (ele, parentEle) {
        var x = Number(ele.style.left.replace("px", ""));
        var y = Number(ele.style.top.replace("px", ""));
        if (parentEle) {
            x += parentEle.scrollLeft;
            y += parentEle.scrollLeft;
        }
        return new ui_linear.vector(x, y);
    },
    getSizeOfEle: function (ele) {
        var x = Number(ele.style.width.replace("px", ""));
        var y = Number(ele.style.height.replace("px", ""));

        return new ui_linear.vector(x, y);
    },
    getRectOfEle: function (ele) {
        var R = ele.getBoundingClientRect();
        var size = ui_html.getSizeOfEle(ele);
        var pos = ui_html.getLeftTopOfEle(ele);
        R.x = pos.x;
        R.y = pos.y;
        R.width = (size.x == 0) ? (R.right - pos.x) : size.x;
        R.height = (size.y == 0) ? (R.bottom - pos.y) : size.y;
        return R;

    },
    browserFile: function (accept) {
        return new Promise > (function (resolve, reject) {
            var F = ui_html.createInput("file");
            if (accept) {
                F.setAttribute("accept", accept)
            }

            F.onchange = evt => {
                resolve(F.files[0])
            };
            F.click();


        });
    },
    getComments: function (ele) {
        var ret = [];
        for (var i = 0; i < ele.childNodes.length; i++) {
            var n = ele.childNodes[i];
            if (n.nodeType == 8) {
                ret.push(n.nodeValue);
            }
        }
        return ret;
    },
    uiReady: function (ele) {
        class runner {
            constructor(ele) {

            }
        }
    },
    getPos: function (ele) {
        if (ele instanceof HTMLElement) {
            var ret = new ui_linear.vector(ele.getBoundingClientRect().x, ele.getBoundingClientRect().y);
            var parent = ele.parentElement;
            while (parent.tagName != "HTML") {
                if (parent.style.position == "absolute" || parent.style.position == "fixed") {
                    return new ui_linear.vector(ele.getBoundingClientRect().x, ele.getBoundingClientRect().y);
                }
                ret.y += parent.scrollTop;
                ret.x += parent.scrollLeft;
                parent = parent.parentElement;
            }
            ret.y += document.body.scrollTop;
            ret.x += parent.scrollLeft;
            return ret;
        }
        if (ele instanceof MouseEvent) {
            var R = ele.target.getBoundingClientRect();
            var ret = new ui_linear.vector(ele.offsetX + R.x, ele.offsetY + R.y);
            var target = ele.target;
            if (target.style.position == "fixed") {
                ret = new ui_linear.vector(ele.offsetX + R.x, ele.offsetY + R.y);
                return ret;
            }
            if (target.style.position == "absolute") {
                ret = new ui_linear.vector(ele.clientX, ele.clientY);

                return ret;
            }
            var parent = target.parentElement;
            while (parent.tagName != "HTML") {
                if (parent.style.position == "fixed") {
                    ret = new ui_linear.vector(ele.offsetX + R.x, ele.offsetY + R.y);
                    return ret;
                }
                if (parent.style.position == "absolute") {
                    ret = new ui_linear.vector(ele.clientX, ele.clientY);
                    return ret;
                }
                else {
                    var _r = parent.getBoundingClientRect();
                    ret.x += _r.x;
                    ret.y += _r.y;
                }
                ret.y += parent.scrollTop;
                ret.x += parent.scrollLeft;
                parent = parent.parentElement;
            }
            ret.y += document.body.scrollTop;
            ret.x += parent.scrollLeft;
            return ret;
        }
    },
    getRect: function (ele) {
        var ret = new ui_linear.rect(ele);
        var r = getPos(ele);
        ret.x = r.x;
        ret.y = r.y;
        return ret;
    }
}
export { ui_html }