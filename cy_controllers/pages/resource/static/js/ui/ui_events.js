
import { ui_linear } from "./ui_linear.js";
import { ui_html } from "./ui_html.js";
class baseEvent {
    ondragstart;
    ondrop;
    oncontextmenu;
    onkeydown;
    onscroll;
    onchange;
    onclick;
    onmousedown;
    onmousemove;
    onmouseup;
    onmouseout;
    onmouseleave;
    onmouseover;
}
class ui_events_handler {

    ele;
    event;
    oldEvents;
    holdEvents;
    filter = {};
    cursor;
    data;
    _isInTrigger;

    constructor(ele, config) {
        this.data = {};
        this.ele = ele;
        this.event = new ui_events.event();
        this.oldEvents = {};
        this.holdEvents = {};
        this.filter = {};
        this.cursor = new ui_events_cursor(this);
        var keys = Object.keys(this.event);
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];
            if (this.ele[key] && this.ele[key] != null) {
                this.oldEvents[key] = this.ele[key];
            }
        }
        if (config)
            this.set(config);
    }
    set(event) {

        var me = this;
        var keys = Object.keys(event);
        for (var i = 0; i < keys.length; i++) {
            if (keys[i] != "filter" && event[keys[i]] != null && event[keys[i]] != undefined) {
                if (this.holdEvents[keys[i]] && this.holdEvents[keys[i]] != null) {
                    this.event[keys[i]] = this.holdEvents[keys[i]]
                }
                else {
                    this.event[keys[i]] = event[keys[i]];

                }
                if (event["filter"]) {
                    this.filter[keys[i]] = event["filter"];
                }
            }
        }
        if (event["forEach"]) {
            var nEvent = event;
            keys = (nEvent.forEach.events);
            for (var i = 0; i < keys.length; i++) {
                if (this.holdEvents[keys[i]] && this.holdEvents[keys[i]] != null) {
                    this.event[keys[i]] = this.holdEvents[keys[i]]
                }
                else {
                    this.event[keys[i]] = nEvent.forEach.do;

                }
                if (nEvent.forEach.filter) {
                    this.filter[keys[i]] = nEvent.forEach.filter;
                }
            }
        }
        this.raiseEvents();
    }
    raiseEvents() {

        var me = this;
        var keys = Object.keys(me.event);
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];
            if (me.event[key] != null && me.event[key] != undefined) {
                this.ele[key] = (evt) => {
                    evt["sender"] = me;
                    var mEvt = evt;
                    this.cursor.x = mEvt.clientX + this.ele.scrollLeft;
                    this.cursor.y = mEvt.clientY + this.ele.scrollTop;
                    if (me.oldEvents["on" + evt.type]) {
                        me.oldEvents["on" + evt.type](evt);
                    }

                    if (me.event["on" + evt.type]) {
                        if (me.filter["on" + evt.type]) {
                            if (me.filter["on" + evt.type](evt)) {
                                me.event["on" + evt.type](evt);
                            }
                        }
                        else {
                            me.event["on" + evt.type](evt);
                        }
                    }
                    var _e = evt;
                    if (this._isInTrigger) {
                        this._isInTrigger = false;
                        _e.stopImmediatePropagation();
                        _e.preventDefault();
                        return true;
                    }
                }
            }
        }

    }
    unset(event) {

        var keys = Object.keys(event);
        for (var i = 0; i < keys.length; i++) {
            this.holdEvents[keys[i]] = this.event[keys[i]];
            this.event[keys[i]] = undefined;
            this.ele[keys[i]] = this.oldEvents[keys[i]]
        }
    }
    trigger(evt, eventsToTrigger) {
        var keys = Object.keys(eventsToTrigger);
        this._isInTrigger = true;
        keys.forEach(k => {
            var n = k.substring(2, k.length);
            var yeah = new Event(n, evt);
            this.ele.dispatchEvent(yeah);
            this._isInTrigger = false;
        });

    }
};
class ui_events_dragger  extends ui_events_handler {
    _startPos;

    _onStarDrag;
    _onStopDrag;
    _orginPos;
    parentEvent;
    enable;
    _constraint;
    constructor(ele, constraint) {
        super(ele);
        ui_html.setStyle(this.ele, {
            position: "absolute"
        });
        this._constraint = constraint;
        this.enable = true;
        this._initEvents();
    }
    _initEvents() {

        var me = this;


        this.set({
            filter: evt => {
                var ret = evt.which == 1 && this.enable;
                if (ret) {
                    if (this._constraint) {
                        if (this._constraint(evt)) {
                            return true;
                        }
                        else {
                            return false;
                        }
                    }
                }
                return ret;
            },
            forEach: {
                events: ["onmousemove"],
                do: evt => {

                }
            },
            onmouseleave: evt => {
                if (!me._startPos) return;
                var pos = ui_html.getClientCoordinate(evt, this.ele.parentNode);
                var delta = pos.subtract(me._orginPos);
            },
            onmousedown: evt => {

                me._startPos = ui_html.getClientCoordinate(evt, me.ele.parentNode); //new q.linear.vector(evt.clientX, evt.clientY);
                me._orginPos = ui_html.getClientCoordinate(evt, me.ele.parentNode);
                if (!this.parentEvent) {
                    this.parentEvent = new q.events.handler(this.ele.parentElement);

                }
                this.parentEvent.set({
                    onscroll: evt => {
                        me._startPos = undefined;

                    },
                    onmousemove: evt => {

                        if (!me._startPos) return;
                        var pos = ui_html.getClientCoordinate(evt, me.ele.parentNode); //new q.linear.vector(evt.clientX, evt.clientY);
                        var delta = pos.subtract(me._startPos);
                        var R = this.ele.getClientRects()[0];//.getBoundingClientRect();
                        var x = Number(this.ele.style.left.replace("px", ""));
                        var y = Number(this.ele.style.top.replace("px", ""));
                        ui_html.setStyle(this.ele, {
                            left: (x + evt.movementX).toString() + "px",
                            top: (y + evt.movementY).toString() + "px"
                        });
                        this._startPos = pos;
                    },
                    onmouseup: evt => {
                        me._startPos = undefined;
                    }
                });
                ui_html.setStyle(me.ele, {
                    cursor: "grabbing",
                    zIndex: "10000",
                    position: "absolute"
                });
                if (this._onStarDrag) {
                    try {
                        this._onStarDrag();
                    } catch (e) {
                        console.error(e);
                    }
                }
            },
            onmouseup: evt => {
                me.parentEvent.unset({
                    onmousemove, onmouseup
                });
                me._startPos = undefined;
                ui_html.setStyle(me.ele, {
                    cursor: "default"
                });
                if (me._onStopDrag) {
                    try {
                        me._onStopDrag();
                    } catch (e) {
                        console.error(e);
                    }
                }
            }
        })
    }
    onStarDrag(cb) {
        this._onStarDrag = cb;
    }
    onStopDrag(cb) {
        this._onStopDrag = cb;
    }
}
class ui_events_event extends baseEvent {
    forEach;
    constructor() {
        super();
        this.forEach = {
            filter: undefined,
            events: undefined,
            do: undefined
        };
        this.onclick = null;
        this.onmousedown = null
        this.onmousemove = null
        this.onmouseup = null
        this.onmouseout = null
        this.onmouseleave = null
    }
};
class ui_events_cursor {
    owner;
    x;
    y;
    constructor(owner) {
        this.owner = owner;
    }
    subtract(pos) {
        return {
            x: this.x - pos.x,
            y: this.y - pos.y
        }
    }
}
var ui_events = {
    baseEvent: baseEvent,
    event: ui_events_event,
    cursor: ui_events_cursor ,
    handler: ui_events_handler,
    dragger: ui_events_dragger,
    draggerRelative: class extends ui_events_dragger {
        constructor(ele, constraint) {
            super(ele, constraint);
            var r = this.ele.parentNode.getBoundingClientRect();
            ui_html.setStyle(this.ele.parentNode, {
                position: "relative",
                overflow: "auto"
                //left: r.x.toString() + "px",
                //top: r.y.toString() + "px"
            });

        }
    },
    resizeEdge: class extends ui_events_handler {
        _handleSize;
        _cursor;
        _starResize;
        _starResizePos;
        _onStarResize;
        _onStopResize;
        enable;
        _constraint;
        constructor(ele, handleSize, constraint) {
            super(ele);
            this._constraint = constraint;
            if (!this._constraint) {
                this._constraint = evt => { return true; };
            }
            this._handleSize = handleSize;
            this._cursor = this.ele.style.cursor || "default";
            this._installEvents();
            this.enable = true;
        }
        onStartResize(cb) {
            this._onStarResize = cb;
        }
        onStopResize(cb) {
            this._onStopResize = cb;
        }
        _installEvents() {
            var me = this;
            me.set({
                filter: evt => {
                    return evt.which == 1 && me.enable && me._constraint(evt);
                },
                forEach: {
                    filter: evt => { return me.enable && me._constraint(evt); },
                    events: ["onmousemove", "onmouseout", "onmouseleave"],
                    do: evt => {
                        if (evt.which == 0)
                            me._detectHandler(evt);
                        else if (evt.which == 1 && me._starResizePos) {
                            var pos = ui_html.getClientCoordinate(evt, me.ele.parentNode);
                            var R = me.ele.getBoundingClientRect();
                            var relPos = ui_html.getLeftTopOfEle(me.ele, me.ele.parentNode);
                            var size = ui_html.getSizeOfEle(me.ele);
                            var delta = pos.subtract(me._starResizePos);
                            if (me._cursor == "w-resize") {
                                ui_html.setStyle(me.ele, {
                                    left: (relPos.x + delta.x).toString() + "px",
                                    width: (size.x - delta.x).toString() + "px"
                                });
                            }
                            if (me._cursor == "n-resize") {
                                ui_html.setStyle(me.ele, {
                                    top: (relPos.y + delta.y).toString() + "px",
                                    height: (size.y - delta.y).toString() + "px"
                                });
                            }
                            if (me._cursor == "e-resize") {
                                ui_html.setStyle(me.ele, {

                                    width: (size.x + delta.x).toString() + "px"
                                });
                            }
                            if (me._cursor == "s-resize") {
                                ui_html.setStyle(me.ele, {

                                    height: (size.y + delta.y).toString() + "px"
                                });
                            }

                            if (me._cursor == "nw-resize") {
                                ui_html.setStyle(me.ele, {
                                    left: (relPos.x + delta.x).toString() + "px",
                                    width: (size.x - delta.x).toString() + "px",
                                    top: (relPos.y + delta.y).toString() + "px",
                                    height: (size.y - delta.y).toString() + "px"
                                });
                            }
                            if (me._cursor == "sw-resize") {
                                ui_html.setStyle(me.ele, {
                                    left: (relPos.x + delta.x).toString() + "px",
                                    width: (size.x - delta.x).toString() + "px",
                                    height: (size.y + delta.y).toString() + "px"
                                });
                            }
                            if (me._cursor == "ne-resize") {
                                ui_html.setStyle(me.ele, {
                                    top: (relPos.y + delta.y).toString() + "px",
                                    height: (size.y - delta.y).toString() + "px",
                                    width: (size.x + delta.x).toString() + "px"
                                });
                            }
                            if (me._cursor == "se-resize") {
                                ui_html.setStyle(me.ele, {

                                    width: (size.x + delta.x).toString() + "px",
                                    height: (size.y + delta.y).toString() + "px"
                                });
                            }
                            me._starResizePos = pos;

                        }

                    }

                },
                onmousedown: evt => {
                    if (me._starResize) {
                        me._starResizePos = ui_html.getClientCoordinate(evt, me.ele.parentNode);
                        if (me._onStarResize) {
                            try {
                                me._onStarResize();
                            } catch (e) {
                                console.error(e);
                            }
                        }
                    }
                },
                onmouseup: evt => {
                    if (me._starResize) {
                        me._starResize = undefined;
                        if (me._onStopResize) {
                            try {
                                me._onStopResize();
                            } catch (e) {
                                console.error(e);
                            }
                        }
                    }
                }
            })

        }
        _detectHandler(evt) {

            var me = this;
            var R = me.ele.getBoundingClientRect();
            var parent = me.ele.parentNode;
            var x = R.x + parent.scrollLeft;
            var y = R.y + parent.scrollTop;
            var d = Math.ceil(this._handleSize / 2);
            var pos = ui_html.getClientCoordinate(evt, me.ele.parentNode);
            me._starResize = false;
            if (x - d < pos.x && pos.x < x + d && y - d < pos.y && pos.y < y + d) {
                me._starResize = true;
                me._cursor = "nw-resize";
                ui_html.setStyle(me.ele, {
                    cursor: me._cursor
                });
                return;
            }
            else if (x - d < pos.x && pos.x < x + d && y + R.height - d < pos.y && pos.y < y + R.height + d) {
                me._starResize = true;
                me._cursor = "sw-resize";
                ui_html.setStyle(me.ele, {
                    cursor: me._cursor
                });
                return;
            }
            else if (x - d < pos.x && pos.x < x + d && y + R.height - d < pos.y && pos.y < y + R.height + d) {
                me._starResize = true;
                me._cursor = "sw-resize";
                ui_html.setStyle(me.ele, {
                    cursor: me._cursor
                });
                return;
            }
            else if (x + R.width - d < pos.x && pos.x < x + R.width + d && y - d < pos.y && pos.y < y + d) {
                me._starResize = true;
                me._cursor = "ne-resize";
                ui_html.setStyle(me.ele, {
                    cursor: me._cursor
                });
                return;
            }
            else if (x + R.width - d < pos.x && pos.x < x + R.width + d && y + R.height - d < pos.y && pos.y < y + R.height + d) {
                me._starResize = true;
                me._cursor = "se-resize";
                ui_html.setStyle(me.ele, {
                    cursor: me._cursor
                });
                return;
            }


            else if (x - d < pos.x && pos.x < x + d) {
                me._starResize = true;
                me._cursor = "w-resize";
                ui_html.setStyle(me.ele, {
                    cursor: me._cursor
                });
                return;
            }
            else if (x + R.width - d < pos.x && pos.x < x + R.width + d) {
                me._starResize = true;
                me._cursor = "e-resize";
                ui_html.setStyle(me.ele, {
                    cursor: me._cursor
                });
                return;
            }
            else if (y - d < pos.y && pos.y < y + d) {
                me._starResize = true;
                me._cursor = "n-resize";
                ui_html.setStyle(me.ele, {
                    cursor: me._cursor
                });
                return;
            }
            else if (y + R.height - d < pos.y && pos.y < y + R.height + d) {
                me._starResize = true;
                me._cursor = "s-resize";
                ui_html.setStyle(me.ele, {
                    cursor: me._cursor
                });
                return;
            }
            me._cursor = "default";
            ui_html.setStyle(me.ele, {
                cursor: me._cursor
            });
        }

    },
    mouseDraw: class extends ui_events_handler {
        start;
        end;
        rectDiv;
        _onStart;
        _onEnd;
        _constraint;
        constructor(ele, constraint) {
            super(ele);
            if (constraint) {
                this._constraint = constraint;
            }
            else {
                this._constraint = evt => {
                    return evt.which == 1;
                };
            }
            this.rectDiv = ui_html.createEle("div");
            ui_html.setStyle(this.rectDiv, {
                position: "absolute",
                borderStyle: "dotted",
                borderWidth: "2px",
                borderColor: "#000",
                display: "none"
            });
            this.ele.appendChild(this.rectDiv);
            this.set({
                filter: this._constraint,
                onmousedown: evt => {
                    //this.start = new q.linear.vector(evt.offsetX + this.ele.scrollLeft, evt.offsetY + this.ele.scrollTop);
                    this.start = new q.linear.vector(evt.offsetX, evt.offsetY);
                    //this.start = ui_html.getClientCoordinate(evt, this.ele);
                    if (this._onStart) {
                        this._onStart(evt);
                        if (!this.start) {
                            return;

                        }

                    }
                },
                forEach: {
                    events: ["onmousemove", "onmouseout"],
                    do: evt => {
                        if (!this.start) return;
                        //this.end = new q.linear.vector(evt.offsetX + this.ele.scrollLeft, evt.offsetY + this.ele.scrollTop);
                        this.end = new q.linear.vector(evt.offsetX, evt.offsetY);
                        //this.end =ui_html.getClientCoordinate(evt, this.ele);
                        var delta = this.end.subtract(this.start);
                        ui_html.setStyle(this.rectDiv, {
                            width: delta.x.toString() + "px",
                            height: delta.y.toString() + "px",
                            left: this.start.x.toString() + "px",
                            top: this.start.y.toString() + "px",
                            display: "block",
                            zIndex: "10000"
                        });
                    }
                },
                onmouseup: evt => {
                    var ret = this.rectDiv.getBoundingClientRect();
                    var pos = ui_html.getLeftTopOfEle(this.rectDiv);
                    ret.x = pos.x;
                    ret.y = pos.y;

                    if (this._onEnd) {

                        this._onEnd(ret);

                    }
                    this.start = undefined;
                    ui_html.setStyle(this.rectDiv, { display: "none" });
                }
            })
        }
        onStart(cb) {
            this._onStart = cb;
        }
        onEnd(cb) {
            this._onEnd = cb;
        }
    }
};
export { ui_events}