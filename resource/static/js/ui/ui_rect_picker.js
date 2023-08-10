import { ui_events } from "./ui_events.js";
import { ui_graph2d } from "./ui_graph2d.js";
import { ui_html } from "./ui_html.js";
const HANDLE_SIZE = 10;
class ui_rect_picker extends ui_html.Rect {
    _timeOutDrawWithHanlde;
    _isSelected;

   async  getImageAsFile(scale) {
       scale = scale || 1;
       var imageData = await this.getImageData(scale);
       var newImgData = ui_graph2d.scaleImageData(imageData, scale);
       var r = await ui_graph2d.grayScale(newImgData);
       var F = await ui_graph2d.createFileFromImageData(newImgData, "test.png");
       return F;
    }
    meta;
    show_tesseract_recognize(data) {

        var R = this.canvas.getBoundingClientRect();
        if (!this.desk.resultWindow) {
            this.desk.resultWindow = new q.UiDesk.WINDOW();
            this.desk.resultTextarea = ui_html.createEle("textarea");

            ui_html.setStyle(this.desk.resultTextarea, {
                width: "100%",
                height: "100%",
                float: "left"
            });
            document.body.appendChild(this.desk.resultTextarea);
            this.desk.resultWindow.setTitle(" ");
            this.desk.resultWindow.setBody(this.desk.resultTextarea);
        }
        this.desk.resultTextarea.innerHTML = data.text;
        var H = R.height + 46;
        if (H > document.body.getBoundingClientRect().height) {
            H = document.body.getBoundingClientRect().height - 46;
        }
        this.desk.resultWindow.size(R.width, H);
        ui_html.setStyle(this.desk.resultTextarea, {
            width: "100%",
            height: (H - 54).toString() + "px",
            float: "left"
        });
        this.desk.resultWindow.show();
    }
    body;
    trackHandlerEvent;
    startResize;

    startResizeEvent;
    resizeStop;
    resizeEventOut;
    currentHandle;
    handles;
    handleSize;
    nwResize;
    nResize;
    neResize;
    wResize
    eResize;
    swResize;
    sResize;
    seResize;
    cEvent = undefined;
    constructor(x, y, w, h) {
        super(x, y, w, h);
        var me = this;
        this.handles = [];
        this.handleSize = HANDLE_SIZE;
        this.handles.push(this.create_nwResize());
        this.handles.push(this.create_nResize());
        this.handles.push(this.create_neResize());
        this.handles.push(this.create_wResize());
        this.handles.push(this.create_eResize());
        this.handles.push(this.create_swResize());
        this.handles.push(this.create_sResize());
        this.handles.push(this.create_seResize());
        //this._initEvents();

    }
    getData() {
        var ret = new DOMRect();
        ret.x = this.x;
        ret.y = this.y;
        ret.width = this.w;
        ret.height = this.h;
        return ret;
    }
    setData(r) {
        this.x = r.x;
        this.y = r.y;
        this.w = r.width;
        this.h = r.height;
    }
    setScale(zoom) {
        this.scaleSize = zoom;
        this.w = this.w / zoom;
        this.h = this.h / zoom;
        this.x = this.x / zoom;
        this.y = this.y / zoom;
    }

    clearDraw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    enableResize() {
        this.attachEvent(this.trackHandlerEvent);
    }
    create_seResize(){
        this.seResize = new ui_html.pickerHandle(this.handleSize);
        this.seResize.x = (this.w + this.handleSize) / 2;
        this.seResize.y = this.h + this.handleSize / 2;
        this.seResize.cursor = "se-resize";
        return this.seResize;
    }
    create_sResize() {
        this.sResize = new ui_html.pickerHandle(this.handleSize);
        this.sResize.x = (this.w + this.handleSize) / 2;
        this.sResize.y = this.h - this.handleSize / 2;
        this.sResize.cursor = "s-resize";
        return this.sResize;
    }
    create_swResize() {
        this.swResize = new ui_html.pickerHandle(this.handleSize);
        this.swResize.x = this.handleSize / 2;
        this.swResize.y = this.h - this.handleSize / 2;
        this.swResize.cursor = "sw-resize";
        return this.swResize;
    }
    create_eResize() {
        this.eResize = new ui_html.pickerHandle(this.handleSize);
        this.eResize.x = 0;
        this.eResize.y = (this.h + this.handleSize) / 2;
        this.eResize.cursor = "e-resize";
        return this.eResize;
    }
    create_wResize() {
        this.wResize = new ui_html.pickerHandle(this.handleSize);
        this.wResize.x = this.w - this.handleSize / 2;
        this.wResize.y = this.handleSize / 2;
        this.wResize.cursor = "w-resize";
        return this.wResize;
    }
    create_neResize(){
        this.neResize = new ui_html.pickerHandle(this.handleSize);
        this.neResize.x = this.w - this.handleSize / 2;
        this.neResize.y = this.handleSize / 2;
        this.neResize.cursor = "ne-resize";
        return this.neResize;
    }
    create_nResize() {
        this.nResize = new ui_html.pickerHandle(this.handleSize);
        this.nResize.x = (this.w - this.handleSize) / 2;
        this.nResize.y = 0;
        this.nResize.cursor = "n-resize";

        return this.nResize;
    }
    create_nwResize() {
        this.nwResize = new ui_html.pickerHandle(this.handleSize);
        this.nwResize.x = 0;
        this.nwResize.y = 0;
        this.nwResize.cursor = "nw-resize";
        return this.nwResize;
    }
    drawWithHandle() {
        var me = this;
        var dw = Math.round(this.w * this.scaleSize);
        var dh = Math.round(this.h * this.scaleSize);
        var x = Math.round(this.x * this.scaleSize);
        var y = Math.round(this.y * this.scaleSize);
        ui_html.setStyle(this.canvas, {
            width: dw.toString() + "px",
            height: dh.toString() + "px",
            left: x.toString() + "px",
            top: y.toString() + "px"
        });
        if (!me.cEvent) {
            me.cEvent = new ui_events.handler(me.canvas);
            me.cEvent.set({
                filter: evt => { return evt.which==1 },
                onmousemove: evt => {
                    console.log(evt);
                    var resizeHandle = me.detectResizeHandleByRelativePos({
                        x: evt.offsetX,
                        y: evt.offsetY
                    });
                    if (resizeHandle) {
                        ui_html.setStyle(me.canvas, {
                            'cursor': resizeHandle.cursor
                        });
                    }
                    else {
                        ui_html.setStyle(me.canvas, {
                            'cursor': 'grabbing'
                        });
                    }

                }
            });
            me.cEvent.set({
                filter: evt => { return evt.which == 0 },
                onmousemove: evt => {
                    
                    var resizeHandle = me.detectResizeHandleByRelativePos({
                        x: evt.offsetX,
                        y: evt.offsetY
                    });
                    if (resizeHandle) {
                        ui_html.setStyle(me.canvas, {
                            'cursor': resizeHandle.cursor
                        });
                    }
                    else {
                        ui_html.setStyle(me.canvas, {
                            'cursor': 'grabbing'
                        });
                    }

                }
            });
            me.cEvent.set({
                onmouseout: evt => {
                    ui_html.setStyle(me.canvas, {
                        'cursor': 'default'
                    });

                }
            });
        }
        
        this.canvas.width = dw;
        this.canvas.height = dh;
        this.ctx.clearRect(0, 0, dw, dh);
        this.ctx.beginPath();
        //this.ctx.strokeStyle = 'red';
        this.ctx.lineDashOffset = 8;
        let offset = 0;
        var me = this;
        function draw() {
            if (me._isSelected) {

                me.ctx.beginPath();
                me.ctx.clearRect(0, 0, me.ctx.canvas.width, me.ctx.canvas.height);
                me.ctx.setLineDash([4, 2]);
                me.ctx.lineDashOffset = -offset;
                me.ctx.lineWidth = 4;
                ui_graph2d.drawRect(me.ctx, 0, 0, me.ctx.canvas.width, me.ctx.canvas.height);
                me.ctx.stroke();
                me.ctx.closePath();
                for (var i = 0; i < me.handles.length; i++) {
                    me.handles[i].draw(me.ctx);
                }
            }

        }

        function march() {
            offset++;
            if (offset > 16) {
                offset = 0;
            }
            draw();
            setTimeout(march, 20);
        }

        this._recalculateHandlesPosition();
        me._isSelected = true;
        march();

    }

    drawWithoutHandle() {
        clearInterval(this._timeOutDrawWithHanlde);
        this._isSelected = false;
        var dw = Math.round(this.w * this.scaleSize);
        var dh = Math.round(this.h * this.scaleSize);
        var x = Math.round(this.x * this.scaleSize);
        var y = Math.round(this.y * this.scaleSize);
        ui_html.setStyle(this.canvas, {
            width: dw.toString() + "px",
            height: dh.toString() + "px",
            left: x.toString() + "px",
            top: y.toString() + "px"
        });
        this.canvas.width = dw;
        this.canvas.height = dh;
        this.canvas.width = dw;
        this.canvas.height = dh;
        this.ctx.clearRect(0, 0, dw, dh);
        this.ctx.beginPath();
        //this.ctx.strokeStyle = 'red';
        this.ctx.lineDashOffset = 8;
        let offset = 0;
        var me = this;
        function draw() {
            if (!me._isSelected) {
                me.ctx.beginPath();
                me.ctx.clearRect(0, 0, me.ctx.canvas.width, me.ctx.canvas.height);
                me.ctx.setLineDash([4, 2]);
                me.ctx.lineDashOffset = -offset;
                me.ctx.lineWidth = 4;
                ui_graph2d.drawRect(me.ctx, 0, 0, me.ctx.canvas.width, me.ctx.canvas.height);
                //me.ctx.rect(1, 1, me.ctx.canvas.width - 2, me.ctx.canvas.height - 2);
                me.ctx.stroke();
                me.ctx.closePath();

            }

        }

        function march() {
            offset++;
            if (offset > 16) {
                offset = 0;
            }
            draw();
            setTimeout(march, 20);
        }

        this._recalculateHandlesPosition();
        march();

    }
    async getImageData(rateScale) {

        var me = this;
        if (me.desk.getPdfObject()) {
            var canvas = me.desk.getBufferCanvas(me.desk.getCurrentPageIndex());
            if (canvas == null) {
                canvas = me.desk.createBufferCanvas(me.desk.getCurrentPageIndex());
                var data = await ui_graph2d.pdfLoadPage(me.desk.getPdfObject(), me.desk.SCALE_BUFFER_SIZE, me.desk.getCurrentPageIndex());
                var R = me.getData();// html.getRectOfEle(this.canvas);
                R = ui_linear.scaleDOMRect(R, rateScale);

                var imgData = data.canvasContext.getImageData(
                    R.x,
                    R.y,
                    R.width,
                    R.height
                );

                return imgData;
            }
            else {
                var R = me.getData();
                R = ui_linear.scaleDOMRect(R, rateScale);
                var imgData = canvas.getContext("2d").getImageData(
                    R.x,
                    R.y,
                    R.width,
                    R.height
                );
                return imgData;
            }
        }
        else {
            var R = me.getData();// html.getRectOfEle(this.canvas);
            R = ui_linear.scaleDOMRect(R, me.desk.getZoomValue() / 100);

            var imgData = me.desk.canvas.getContext("2d").getImageData(
                R.x,
                R.y,
                R.width,
                R.height
            );
            return imgData;
        }


    }
    async getImageBase64(rateScale, cb) {
        var imgdata = await this.getImageData(rateScale);
        
        var tmpCanvas = ui_html.createEle("canvas");
        tmpCanvas.width = imgdata.width;
        tmpCanvas.height = imgdata.height;
        var tmpContext = tmpCanvas.getContext("2d");
        var r = await ui_graph2d.grayScale(imgdata);
        var r2 = await ui_graph2d.contrastImage(r, 100);
        tmpContext.putImageData(r, 0, 0);
        var ret = q.resources.urlFromImageBase64Text(tmpCanvas.toDataURL('image/jpeg', 1.0));
        return ret;
    }
    async getImageUrl(rateScale) {
        return await this.getImageBase64(rateScale);

    }
    async tesseract_recognize() {
        return await this.desk.tesseract_recognize(this);
    }
    _recalculateHandlesPosition() {
        this.neResize.x = this.scaleSize * this.w - this.handleSize;
        this.neResize.y = 0;
        this.nResize.x = this.scaleSize * this.w / 2 - this.handleSize / 2;
        this.nwResize.x = 0;
        this.nwResize.y = 0;
        this.seResize.x = this.scaleSize * this.w - this.handleSize;
        this.seResize.y = this.scaleSize * this.h - this.handleSize;
        this.sResize.x = this.scaleSize * this.w / 2 - this.handleSize / 2;
        this.sResize.y = this.scaleSize * this.h - this.handleSize
        this.swResize.x = 0;
        this.swResize.y = this.scaleSize * this.h - this.handleSize;
        this.wResize.x = 0;

        this.eResize.x = this.scaleSize * this.w - this.handleSize;
        this.wResize.y = this.eResize.y = this.scaleSize * this.h / 2 - this.handleSize / 2;
    }
    detectResizeHandleByRelativePos(pos) {
        var me = this;
        
        
        
        var R = me.canvas.getBoundingClientRect();
        for (var i = 0; i < me.handles.length; i++) {
            var hanle = me.handles[i];
            var x1 = hanle.x ;
            var y1 =hanle.y ;
            var x2 = hanle.x + me.handleSize ;
            var y2 = hanle.y + me.handleSize ;
            if (x1 < pos.x && pos.x < x2 && y1 < pos.y && pos.y < y2) {
                return hanle;
            }
        }

    }
    detectResizeHandle(pos) {
        var me = this;
        if ((!me.canvas) || me.canvas == null || me.canvas.parentElement == null) {
            return;
        }
        var sx = me.canvas.parentElement.scrollLeft;
        var sy = me.canvas.parentElement.scrollTop;
        var R = me.canvas.getBoundingClientRect();
        for (var i = 0; i < me.handles.length; i++) {
            var hanle = me.handles[i];
            var x1 = R.x + hanle.x + sx;
            var y1 = R.y + hanle.y + sy;
            var x2 = R.x + hanle.x + me.handleSize + sx;
            var y2 = R.y + hanle.y + me.handleSize + sy;
            if (x1 < pos.x && pos.x < x2 && y1 < pos.y && pos.y < y2) {
                return hanle;
            }
        }
        
    }
    scale(rate) {
        this.scaleSize = rate;

        this._recalculateHandlesPosition();
        this.drawWithHandle()

    }
};
export { ui_rect_picker}