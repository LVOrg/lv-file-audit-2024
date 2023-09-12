import { ui_component, ui_container }  from "./ui_component.js";
import { ui_html } from "./ui_html.js";
import { ui_resource } from "./ui_resource.js";
import { ui_events } from "./ui_events.js";
import { ui_linear } from "./ui_linear.js";
import { ui_layouts } from "./ui_layouts.js";
var defaultConfig = {
    toolbar: {
        item: {
            width: "32px"
        },
        height: "32px"
    },
    window: {
        close_icon: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAAGYktHRAD/AP8A/6C9p5MAAACySURBVFhH7ZYJCsMgEEW19z+Cih5AvZh3sPniQCALo5Da0nkQXDLkP0gyqOuGWsirj8sQAREQARFgC2itlbW2r65xzrVaNmjFHLZwtOzqve87R0IIrQa1XNgCgALOJO7u3TEkACgIIzEbDoYFAAXGGGvO+SA0wpQASCm1YFyYz7L8N/y9V0Dh+0Dae/wjPAsnZiXYAssbER5sjOmra0iUi5yKRUAEvk+glNJnn+Hf+4BSb/17qvNmXT3rAAAAAElFTkSuQmCC'
    },
    boxShadow: "rgba(149, 157, 165, 0.2) 0px 8px 24px",
    windowBodyColor: "rgb(204, 204, 204)",
    windowShadow: "rgba(149, 157, 165, 0.2) 0px 8px 24px"
};
var windManager = [];
class WINDOW_SENDER {
    window;
    index;
    done() {
        this.window.show();
    }
}

class ui_window extends ui_container {
    _footer;
    _footerSpace;
    _footerButtonRegion;
    _onShow;
     _onBeforeOpen;
     _onBeforeClose;
     _onAfterClose;
     _onMove;
    destroy() {
        this.getEle().remove();
    }
    width;
    height;
    _header;
    _bodyWind;
    _title;
    _close;
    _starDrag;
    _resizeable;
    _onResize;
    _frame;
    _draggable = true;
    _windowSize;
    _titleSpan;
    _winBodyEle;
    _isFisrShow = true;
    constructor() {
        super();
        this._onShow = [];
        this._onBeforeOpen = [];
        this._onBeforeClose = [];
        this._onAfterClose = [];
        this._onMove = [];
        var newWindmanager = [];
        for (var i = 0; i < windManager.length; i++) {
            if (document.body.contains(windManager[i].getEle())) {
                newWindmanager.push(windManager[i]);
            }
        }
        newWindmanager.push(this);
        windManager = newWindmanager;
        this._frame = new ui_container();

        this._frame.dock();
        this._frame.getEle().setAttribute("class", "q-window-frame");
        this._frame.setContainer(this);
        this._frame.layoutColumns();
        this._bodyWind = new ui_container();

        this._frame.dock();
        this._header = new ui_container();
        this._header.layoutRows();
        this._header.getEle().setAttribute("class", "header");
        this._header.css({
            height: "32px",
            padding:"0"
            //marginTop:"20px"
        });
        this.undraggable();
        this._title = new ui_container();
        this._title.getEle().setAttribute("class", "title");
        this._windowSize = new ui_container();
        this._windowSize.layoutRows();

        this._title.setContainer(this._header);
        this._windowSize.setContainer(this._header);
        this._titleSpan = ui_html.createEle("span");
        this._title.getEle().appendChild(this._titleSpan);
        this._titleSpan.innerHTML = "";
        ui_html.unselectable(this._title.getEle());

        this._title.dock();
        this._close = ui_html.createEle("img");

        this._close.setAttribute("src", ui_resource.urlFromImageBase64Text(defaultConfig.window.close_icon));
        this._close.setAttribute("ondragstart", "return false;");
        this._close.setAttribute("ondrop", "return false;");
        this._title.getEle().setAttribute("ondragstart", "return false;");
        this._title.getEle().setAttribute("ondrop", "return false;");

        this._windowSize.getEle().appendChild(this._close);
        this._header.setContainer(this._frame);
        this._bodyWind.setContainer(this._frame);
        this._bodyWind.getEle().setAttribute("class", "body");
        this._footer = new ui_container();
        this._footer.getEle().setAttribute("class", "footer");
        this._footer.layoutRows();
        this._footer.setContainer(this._frame);
        this._footer.css({
            padding: "4px",
            display: "none",
            borderTop: "solid 1px",
            borderTopColor: defaultConfig.windowBodyColor
        });
        this._footerSpace = new ui_container();
        this._footerSpace.setContainer(this._footer);
        this._footerSpace.dock();
        this._footerButtonRegion = new ui_container();
        this._footerButtonRegion.setContainer(this._footer);
        this.css({
            position: "absolute",
            display: "none",
            zIndex: "10000",
            backgroundColor: "#fff",

        });
        document.body.appendChild(this.getEle());
        this._format();
        this._installEvent();

    }
    async _raiseEvents(events, next) {
        var ret = true;
        for (var i = 0; i < events.length; i++) {
            
            ret = await events[i]();
            if (!ret) break;
        }

        return ret;
    }
    setTitleEle(ele) {
        if (this._titleSpan) {
            this._titleSpan.remove();
        }
        this._titleSpan = ele;
        this._title.getEle().appendChild(this._titleSpan);
        this._formatTitleSpan();

    }
    _formatTitleSpan() {
        ui_html.setStyle(this._titleSpan, {
            marginTop: "auto",
            marginBottom: "auto",
            marginLeft: "8px",
            whiteSpace: "nowrap",
            textOverflow: "ellipsis",
            overflow: "hidden"

        });
    }
    open() {

        this._raiseEvents(this._onBeforeOpen, () => {
            var sender = new WINDOW_SENDER();
            sender.window = this;
            this.show();
        });
    }
    onBeforeOpen(cb) {
        this._onBeforeOpen.push(cb);
    }
    setFooter(footer) {
        this._footerButtonRegion.getEle().innerHTML = "";
        q.layouts.layoutRows(footer);
        this._footerButtonRegion.getEle().appendChild(footer);
        this._footer.css({
            display: "flex"
        });
    }
    async onResize(asyncCallback) {
        this._onResize = asyncCallback;
    }
    async onBeforeClose(asyncCallback) {
        this._onBeforeClose.push(asyncCallback);
    }
    async onAfterClose(asyncCallback) {
        this._onAfterClose.push(asyncCallback);
    }
    _format() {
        this.css({

            padding: "0px",
            boxShadow: defaultConfig.boxShadow,
            border: "solid 1px #ccc",
        });
        this._header.css({
            borderBottom: "solid 1px #ccc",

        });
        ui_html.setAttrs(this.getEle(), {
            class: "q-window"
        });
        this.css({

            display: "none"
        });
        this._title.layoutRows();
        this._title.css({
            overflow: "hidden"
        });
        ui_html.setStyle(this._titleSpan, {
            marginLeft: "8px",
            marginTop: "auto",
            marginBottom: "auto",
            textOverflow: "ellipsis",
            overflow: "hidden",
            whiteSpace: "nowrap"


        });
    }
    _installEvent() {
        var me = this;
        async function runRaiseEvents() {
            var ret = true;
            for (var i = 0; i < me._onBeforeClose.length; i++) {
                ret = await me._onBeforeClose[i]();
                if (!ret) break;
            }
            return ret;
        }
        new ui_events.handler(this._close).set({
            onclick: evt => {
                runRaiseEvents()
                    .then(r => {
                        if (!r) return;
                          
                            me.css({
                                display: "none"
                            });
                            me._onAfterClose.forEach(f => {
                                f().then();
                            });
                    })
            }
        });
        this._header.setEvent({
            filter: (evt) => {
                return true;
                // return evt.which == 1 && this._draggable;
            },
            forEach: {
                events: ["onmousemove", "onmouseout"],
                do: evt => {
                    if (evt.which == 0) {
                        var R = this._header.getEle().getBoundingClientRect();

                        if (R.x + 10 < evt.clientX &&
                            evt.clientX < R.x + R.width - 10 &&
                            R.y + 10 < evt.clientY &&
                            evt.clientY < R.y + R.height - 10) {
                            this._header.css({
                                cursor: "grabbing"
                            });
                        }
                        else if (R.y - 10 < evt.clientX && R.y < R.y + R.width + 10) {
                            this._header.css({
                                cursor: "n-resize"
                            });
                        }
                        else {
                            this._header.css({
                                cursor: "default"
                            });
                        }
                    }
                    if (evt.which == 1) {
                        if (evt.clientX <= 0 ||
                            evt.clientY <= 0 ||
                            evt.clientX >= window.innerWidth ||
                            evt.clientY >= window.innerHeight
                        ) {
                            this._starDrag = undefined;
                            return;
                        }
                        if (this._starDrag) {

                            var pos = ui_html.getClientCoordinate(evt, this.getEle().parentNode);
                            var delta = pos.subtract(this._starDrag);
                            var R = this.getEle().getBoundingClientRect();
                            var x = Number(this.getEle().style.left.replace("px", ""));
                            var y = Number(this.getEle().style.top.replace("px", ""));
                            var bR = new ui_linear.vector(window.innerWidth, window.innerHeight);
                            var wR = this.getEle().getBoundingClientRect();
                            wR.x += delta.x;
                            wR.y += delta.y;
                            var newPos = new ui_linear.vector(x, y).add(delta);
                            if (wR.y < 0) {
                                newPos.y = 0;
                            }
                            if (wR.x < 0) {
                                newPos.x = 0;
                            }
                            if (newPos.x + R.width >= window.innerWidth) {
                                newPos.x = window.innerWidth - R.width
                            }
                            if (newPos.y + R.height >= window.innerHeight) {
                                newPos.y = window.innerHeight - R.height;
                                var HR = this._header.getEle().getBoundingClientRect();
                                var test = new ui_linear.vector(HR.y + HR.height, evt.clientY)
                                if (test.x < test.y) {
                                    this._starDrag = undefined;
                                    this.css({
                                        left: (newPos.x).toString() + "px",
                                        top: (newPos.y).toString() + "px"
                                    });
                                    return;
                                }
                            }
                            this.css({
                                left: (newPos.x).toString() + "px",
                                top: (newPos.y).toString() + "px"
                            });
                            this._starDrag = pos;
                        }
                    }
                }
            }
        });
        this._header.setEvent({
            filter: evt => {
                return evt.which == 1;
            },
            onmousedown: evt => {
                var R = this._header.getEle().getBoundingClientRect();
                if (R.x + 10 < evt.clientX &&
                    evt.clientX < R.x + R.width - 10 &&
                    R.y + 10 < evt.clientY &&
                    evt.clientY < R.y + R.height - 10) {
                    this._draggable = true;
                    this._starDrag = ui_html.getClientCoordinate(evt, this.getEle().parentNode);
                    this._header.css({
                        cursor: "grabbing"
                    });
                }

            },
            onmouseup: evt => {
                var me = this;
                me._draggable = false;
                me._starDrag = undefined;
                me._header.css({
                    cursor: "default"
                });
                me._onMove.forEach(f => {
                    f(me.getEle().getBoundingClientRect())
                });
            },

        });
        this._resizeable = new ui_events.resizeEdge(this.getEle(), 20);
        this._resizeable.onStartResize(() => {
            
            this._draggable = false;
            this._starDrag = undefined;
        });
        
        this._resizeable.onStopResize(() => {
            console.log(this._raiseOnResize);
            this._draggable = true;
            this._raiseOnResize().then();
        });
        this.setEvent({
            onclick: evt => {
                me.setOnTop();
            }
        })
    }
    setOnTop() {
        var me = this;
        windManager.forEach(w => {
            if (w != me) {
                w.css({
                    zIndex: "1"
                });
            }
            else {
                w.css({
                    zIndex: "200"
                });
            }
        });
    }
    onMove(cb) {
        this._onMove.push(cb);
    }
    setBody(ele) {
        this._winBodyEle = ele;
        ui_html.setStyle(ele, {
            position: "absolute",
            left: "-1000px",
            top: "-1000px",
            float: "left"
        });
        document.body.appendChild(this._winBodyEle);
        var R = window.getComputedStyle(ele);//.getBoundingClientRect();
        ui_html.setAttrs(ele, {
            onselectstart: "return false"
        });

        if (this._isFisrShow) {
            this.width = this.width || Number(R.width.replace("px", ""));

            this.height = Number(R.height.replace("px", "")) + 36;

            this.width = Math.ceil(this.width) + 10;
            this.height = Math.ceil(this.height) + 16;
        }
        this.css({
            height: this.height.toString() + "px",
            width: (this.width) + "px"

        });
        /*this._bodyWind.layoutColumns();*/
        this._bodyWind.getEle().innerHTML = "";
        this._bodyWind.getEle().appendChild(ele);



        this._bodyWind.dock();
        this._bodyWind.css({
            overflow: "hidden"
        });
        ui_html.setStyle(ele, {
            position: "unset",
            left: "unset",
            top: "unset",
            float: "unset",
            zIndex: "0"
            //width: "100%",
            //height: (this.height - 40).toString() + "px"
        });
        this._bodyWind.css({
            padding: "4px",
            zIndex: "1"
        });
        this._bodyWind.layoutColumns();
        ui_layouts.dockFull(this._winBodyEle);
    }
    onShow(cb) {
        console.log(this._onShow);
        this._onShow.push(cb);
    }
    hide() {
        this.css({
            display: "none"

        });
    }
    show(x, y) {
        var me = this;
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                me._show(x, y);
                resolve(me);
            }, 10);
        });
        
    }
    _show(x, y) {
        if ((x !== undefined && y !== undefined) ||
            this._isFisrShow) {
            //var R = new ui_linear.vector(window.innerWidth, window.innerHeight);
            var style = window.getComputedStyle(document.body);
            var sx = document.body.scrollLeft;
            var sy = document.body.scrollTop;
            var bodyRect = document.body.getBoundingClientRect();
            var R = new ui_linear.vector(bodyRect.width, bodyRect.height);

            x = x || ((window.innerWidth - this.width) / 2 + sx);
            y = y || ((window.innerHeight - this.height) / 2 + sy);

            this.css({
                left: x.toString() + "px",
                top: y.toString() + "px",
                display: "block",
                zIndex: "1"

            });
            this.setOnTop();
            this._isFisrShow = false;
        }
        else {
            this.css({
                display: "block",
                zIndex: "1"

            });
            this.setOnTop();
        }
        var me = this;
        this._raiseEvents(this._onShow).then(r => {
            if (!r) return;
            document.body.appendChild(me.getEle());
            me.setOnTop();
        })
           
    }
    setTitle(title) {
        this._titleSpan.innerHTML = title;
    }
    size(width, height) {
        this.css({
            width: width.toString() + "px",
            height: height.toString() + "px"

        });
        this.width = width;
        this.height = height;
        this._raiseOnResize();

    }
    async _raiseOnResize() {
        
        var style = window.getComputedStyle(this._bodyWind.getEle(), null);
        var h = Number(style.getPropertyValue("height").replace("px", ""));
        var w = Number(style.getPropertyValue("width").replace("px", ""));
        
        if (this._onResize) {
            await this._onResize(w, h);
        }
    }
    doMaximize() {
        var R = this.getEle().parentElement.getBoundingClientRect();
        this.show(10, 10)
        this.size(R.width - 20, R.height - 20);
        this.width = R.width - 20;
        this.height = R.height - 20;
    }

}

export {ui_window}