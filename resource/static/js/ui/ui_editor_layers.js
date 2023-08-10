import { ui_linear } from "./ui_linear.js";
import { ui_events } from "./ui_events.js";
import { ui_html } from "./ui_html.js";
import { ui_style } from "./ui_style.js";
class ui_editor_layers_layer  {
    _ele;
    _owner;
    _ownerEvent;
    _start;
    _eleEvent;
    _end;
    _onEnd;
    _isActive;
    _allow;
    _onStart;
    _constraint;
    _desLayer;
    constructor(ele, deskLayer, constraint) {
        this._constraint = constraint;
        this._ele = ui_html.createEle("div");
        this._owner = ele;
        this._desLayer = deskLayer;
        this._eleEvent = new ui_events.handler(this._ele);
        this._ownerEvent = new ui_events.handler(this._owner);
        this._initLayer();
    }
    setConstraint(cb) {
        this._constraint = cb;
    }
    convertToDeskCoordinate(R) {
        //var ret = new DOMRect(R.x, R.y, R.left, R.height);
        R.x += this._desLayer.scrollLeft;
        R.y += this._desLayer.scrollTop;
        return R;
    }
    _initLayer() {
        var R = this._owner.getBoundingClientRect();
        this._ele.setAttribute("data-layer", "draw-rect");
        ui_html.setStyle(this._ele, {
            position: "absolute",
            margin: "0px",
            padding: "0px",
            left: "0x",
            top: "0px",
            width: (R.width).toString() + "px",
            height: (R.height).toString() + "px",
            zIndex: "10000",
            display: "none"
        });
        this._owner.appendChild(this._ele);

    }
    _active() {

        ui_html.setStyle(this._ele, {
            display: "block",
            zIndex: "10000"
        });
    }
    _deactive() {

        ui_html.setStyle(this._ele, {
            display: "none"
        });
    }
    disable() {
        this._allow = false;
        this._deactive();
    }
    enable() {
        this._allow = true;
        this._active();
    }
};
class ui_editor_layers_layers {
    editLayer;
    eleView;
    listOfLayers;
    constructor(eleView) {
        this.listOfLayers = [];
        this.editLayer = ui_html.createEle("div");
        this.eleView.appendChild(this.editLayer);
        this.eleView = eleView;
        this._format();

    }
    _format() {
        ui_html.setStyle(this.editLayer, {
            overflow: "auto",
            width: "100%",
            height: "100%"
        });
    }
};
class ui_editor_layers_rect extends ui_editor_layers_layer {
    start;
    end;
    offset;
    _rectDiv;
    _allowOverlay=true;
    /**
     * *Cho phép draw overlay trên vùng đang chọn
     * @param {any} ofOff
     */
    allowOverlay(onOff) {
        this._allowOverlay = onOff;
    }
    constructor(ele, deskLayer, constraint) {
        super(ele, deskLayer, constraint);
        var me = this;
        this._rectDiv = ui_html.createEle("div");
        ui_html.setStyle(this._rectDiv, {
            borderStyle: "solid",
            borderWidth: "2px",
            borderColor: "red",
            display: "none",
            position: "absolute"
        });
        this._rectDiv.setAttribute("draggable", "false");
        this._ele.appendChild(this._rectDiv);

        this._ownerEvent.set({
            filter: evt => { return evt.which == 1 && this._allow; },
            onmousedown: evt => {
                
                
                this.startDraw(evt);
            }, onmouseup: evt => {
                
                if (this._constraint) {
                    if (!this._constraint(evt)) {
                        this._start = undefined;
                        this._deactive();
                        return;
                    }
                }
                this.end = ui_html.getClientCoordinate(evt, this._owner);
                this.offset = this.end.subtract(this.start);
                var R = ui_html.getRectOfEle(this._rectDiv);
                R = super.convertToDeskCoordinate(R);

                if (Math.abs(this.offset.x) < 10 && Math.abs(this.offset.y) < 10) {
                    this._deactive();
                    return;
                }
                this._start = undefined;
                if (this._onEnd) {
                    this._onEnd(R, this._rectDiv);
                }
                if (me._allowOverlay) {
                    this._deactive();
                }
            }, onmouseout: evt => {
                var R = this._owner.getBoundingClientRect();
                var P = ui_html.getClientCoordinate(evt, this._owner);
                var isIn = R.x < P.x && P.x < R.x + R.width && R.y < P.y && P.y < R.y + R.height;
                if (!isIn) {
                    this._start = undefined;

                    this._deactive();
                }

            }
        });

        this._eleEvent.set({
            filter: evt => { return evt.which == 1 && this._allow; },
            forEach: {
                filter: evt => { return evt.which == 1 && this._allow; },
                events: ["onmousemove", "onmouseout"],
                do: evt => {
                    if (!this._start) return;
                    var R = this._ele.getBoundingClientRect();
                    this._end = ui_html.getClientCoordinate(evt, this._owner);
                    //new ui_linear.vector(evt.clientX, evt.clientY);
                    var delta = this._end.subtract(this._start);
                    if (delta.x < 0 || delta.y < 0) {
                        ui_html.setStyle(this._rectDiv, {
                            left: (this._end.x - R.x) + "px",
                            top: (this._end.y - R.y) + "px",
                            width: Math.abs(delta.x) + "px",
                            height: Math.abs(delta.y) + "px",
                            display: "block"
                        });
                    }
                    else {
                        ui_html.setStyle(this._rectDiv, {
                            left: (this._start.x - R.x) + "px",
                            top: (this._start.y - R.y) + "px",
                            width: delta.x + "px",
                            height: delta.y + "px",
                            display: "block"
                        });
                    }
                }
            }
        })

    }
    startDraw(evt) {
        if (this._constraint) {
            if (!this._constraint(evt)) {
                this._deactive();
                return;
            }
        }
        this.enable();
        this._start = ui_html.getClientCoordinate(evt, this._owner);
        this.start = new ui_linear.vector(this._start.x, this._start.y);
        this._active();
        if (this._onStart) {
            this._onStart();
        }
    }

    onStart(cb) {
        this._onStart = cb;
    }
    onEnd(cb) {
        this._onEnd = cb;

    }
    _deactive() {
        super._deactive();
        ui_html.setStyle(this._rectDiv, {
            display: "none"
        });

    }
    setRectStyle(css) {
        ui_html.setStyle(this._rectDiv, {
            borderStyle: css.borderStyle,
            borderWidth: css.borderWidth,
            borderColor: css.borderColor,
            border: css.border

        });
    }


    trigger(evt, eventsToTrigger) {
        this._ownerEvent.trigger(evt, eventsToTrigger);
    }
};
class ui_editor_layers_dragger extends ui_editor_layers_layer {
    start;
    end;
    _draggEle;
    from;
    constructor(ele, deskLayer) {
        super(ele, deskLayer);
        var me = this;
        me._eleEvent.set({
            filter: evt => { return evt.which == 1 && this._allow; },
            forEach: {
                filter: evt => { return evt.which == 1 && this._allow; },
                events: ["onmousemove", "onmouseout"],
                do: evt => {
                    if (!me.start) {
                        

                    }
                    var R = ui_html.getLeftTopOfEle(me._draggEle);
                    me.end = ui_html.getClientCoordinate(evt, me._owner);
                    //new ui_linear.vector(evt.clientX, evt.clientY);
                    var delta = me.end.subtract(me.start);
                    R = R.add(delta);

                    ui_html.setStyle(me._draggEle, {
                        left: (R.x) + "px",
                        top: (R.y) + "px"
                    });
                   
                    me.start = me.end;

                }
            },
            onmouseup: evt => {

                me.start = undefined;
                if (me._onEnd) {
                    var R = ui_html.getRectOfEle(me._draggEle);
                    R = me.convertToDeskCoordinate(R);
                    ui_html.setStyle(me._draggEle, {
                        left: R.x + "px",
                        top: R.y + "px"
                    });
                   
                    me._onEnd(R, me._draggEle);
                }
                
                me._deactive();
            }
        })
        me._initLayer();
    }

    startDrag(evt, ele) {
        this.enable();
        if (this._ele == ele) return;
        this.start = ui_html.getClientCoordinate(evt, this._owner);
        var R = ui_html.getRectOfEle(ele);
        ui_html.setStyle(ele, {
            left: (R.x - this._desLayer.scrollLeft) + "px",
            top: (R.y - this._desLayer.scrollTop) + "px"

        });
        
        this._ele.appendChild(ele);

        this.from = new ui_linear.vector(this.start.x, this.start.y);
        this._draggEle = ele;

        this._active();
        if (this._onStart) {
            this._onStart();
        }

    }

    onStart(cb) {
        this._onStart = cb;
    }
    onEnd(cb) {
        this._onEnd = cb;
    }
};
class ui_editor_layers_resize extends ui_editor_layers_layer {
    end;
    offset;
    start;
    _currentEle;
    cursor;
    _onResize;
    constructor(ele, deskLayer) {
        super(ele, deskLayer);
        var me = this;
        me._eleEvent.set({
            filter: evt => { return evt.which == 1 && me._allow; },
            onmousemove: evt => {
                var R = ui_html.getRectOfEle(me._currentEle);
                me._end = ui_html.getClientCoordinate(evt, me._ele);
                var delta = me._end.subtract(me._start);
                if (me.cursor == "e-resize") {
                    ui_html.setStyle(me._currentEle, {
                        width: Math.ceil(R.width + delta.x) + "px"
                    });
                }
                if (me.cursor == "s-resize") {
                    ui_html.setStyle(me._currentEle, {
                        height: Math.ceil(R.height + delta.y) + "px"
                    });
                }
                if (me.cursor == "w-resize") {
                    ui_html.setStyle(me._currentEle, {
                        left: Math.ceil(R.x + delta.x) + "px",
                        width: Math.ceil(R.width - delta.x) + "px"
                    });
                }
                if (me.cursor == "n-resize") {
                    ui_html.setStyle(me._currentEle, {
                        top: Math.ceil(R.y + delta.y) + "px",
                        height: Math.ceil(R.height - delta.y) + "px"
                    });
                }

                if (me.cursor == "ne-resize") {
                    ui_html.setStyle(me._currentEle, {
                        top: Math.ceil(R.y + delta.y) + "px",
                        height: Math.ceil(R.height - delta.y) + "px",
                        width: Math.ceil(R.width + delta.x) + "px"
                    });
                }
                if (me.cursor == "se-resize") {
                    ui_html.setStyle(me._currentEle, {
                        height: Math.ceil(R.height + delta.y) + "px",
                        width: Math.ceil(R.width + delta.x) + "px"
                    });
                }
                if (me.cursor == "nw-resize") {
                    ui_html.setStyle(me._currentEle, {
                        top: Math.ceil(R.y + delta.y) + "px",
                        height: Math.ceil(R.height - delta.y) + "px",
                        left: Math.ceil(R.x + delta.x) + "px",
                        width: Math.ceil(R.width - delta.x) + "px"
                    });
                }
                if (me.cursor == "sw-resize") {
                    ui_html.setStyle(me._currentEle, {
                        height: Math.ceil(R.height + delta.y) + "px",
                        left: Math.ceil(R.x + delta.x) + "px",
                        width: Math.ceil(R.width - delta.x) + "px"
                    });
                }
                if (me._onResize) {
                    R = ui_html.getRectOfEle(me._currentEle)
                    me._onResize(R, me._currentEle);
                }
                me._start = me._end;
                ui_html.setStyle(document.body, {
                    cursor: me.cursor
                });
                R = ui_html.getRectOfEle(me._currentEle);

            },
            onmouseup: evt => {
                me._start = undefined;
                var R = ui_html.getRectOfEle(me._currentEle);
                R = me.convertToDeskCoordinate(R);
                
                if (me._onEnd) {
                    me._onEnd(R, me._currentEle);
                }
                me._deactive();
            }

        })
        me._initLayer();
    }

    onStart(cb) {
        this._onStart = cb;
    }
    onEnd(cb) {
        this._onEnd = cb;
    }
    onReszie(cb) {
        this._onResize = cb;
    }
    startResize(evt, ele, cursor) {
        this._start = ui_html.getClientCoordinate(evt, this._ele);
        this.cursor = cursor;
        this.enable();
        this._currentEle = ele;
        var R = ui_html.getRectOfEle(ele);

        ui_html.setStyle(this._currentEle, {
            left: (R.x - this._desLayer.scrollLeft) + "px",
            top: (R.y - this._desLayer.scrollTop) + "px",

        });
        this._ele.appendChild(this._currentEle);
        this._active();
        if (this._onStart) {
            this._onStart();
        }
    }

}
var  ui_editor_layers = {
    layer: ui_editor_layers_layer,
    layers: ui_editor_layers_layers  ,
    rect: ui_editor_layers_rect ,
    dragger: ui_editor_layers_dragger ,
    resize: ui_editor_layers_resize 
}
export { ui_editor_layers }