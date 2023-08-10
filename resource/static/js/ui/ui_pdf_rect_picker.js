/**
 * Cong cu chon vung
 * */

import { ui_html } from "./ui_html.js";
import { ui_graph2d } from "./ui_graph2d.js";
import { ui_desk } from "./ui_desk.js"
import { ui_events } from "./ui_events.js"
import { ui_rect_picker } from "./ui_rect_picker.js";
import { ui_linear } from "./ui_linear.js";
import { ui_resource } from "./ui_resource.js";

const KEY_DELETE_CODE = 46
const EVENT_ON_BEFORE_DELETE_REGION = "event_on_before_delete_region"
const EVENT_ON_BEFORE_BROWSER_FILE = "event_on_before_broser_file"
const EVENT_ON_LOAD_FILE_COMPLETE = "event_on_load_file_complete"
const EVENT_ON_LOADING_FILE = "event_on_loading_file"
const EVENT_RECT_DRAW_BEGIN = "EVENT_RECT_DRAW_BEGIN"
const EVENT_RECT_DRAW_END = "EVENT_RECT_DRAW_END"
class EditorEvents {
    handlers={}
    constructor() {

    }
    /**
     * Trước khi xóa
     * @param {any} asyncCallback
     */
    onBeforeDeleteRegion(asyncCallback) {
        this.handlers[EVENT_ON_BEFORE_DELETE_REGION] = asyncCallback
    }
    /**
     * Trước khi người dùng mở file
     * @param {any} asyncCallback
     */
    onBeforeBrowserFile(asyncCallback) {
        
        this.handlers[EVENT_ON_BEFORE_BROWSER_FILE] = asyncCallback
    }
    onLoadFileComplete(asyncCallback) {
        this.handlers[EVENT_ON_LOAD_FILE_COMPLETE] = asyncCallback
    }
    /**
     * Đang load file example onLoadingFile(async (percent)=>{...})
     * @param {any} asyncCallback
     */
    onLoadingFile(asyncCallback) {
        this.handlers[EVENT_ON_LOADING_FILE] = asyncCallback
    }
    onRectDrawBegin(syncCallback) {
        this.handlers[EVENT_RECT_DRAW_BEGIN] = syncCallback;
    }
    onRectDrawEnd(syncCallback) {
        this.handlers[EVENT_RECT_DRAW_END] = syncCallback;
    }
}
class ui_pdf_rect_picker {

    _accept = "image/*,application/pdf";
    SCALE_BUFFER_SIZE = 2;
    bufferCanvas = {};
    events = new EditorEvents()
    /**
     * Thay doi file, vẫn giữ nguyên các vùng đang sửa
     * */
    async changeFile() {
        var me = this;
        var f = await ui_html.browserFile(this._accept);
        var urlOfFile = URL.createObjectURL(f);
        this._File = f;
        var fileType = f.type;
        this._originFile = f;
        try {
            var me = this;

            me.urlOfFile = urlOfFile;

            me.fileType = (fileType == null || fileType == undefined) ? "" : fileType;
            if (me.fileType.indexOf("image/") > -1) {
                me.isPdf = false;

                me.pdf = undefined;

                if (me.fileType == "image/tiff") {
                    ui_graph2d.convertTIFToPngFile(me._originFile).then(f => {
                        me._File = f;
                        me._originFile = f;
                        me.urlOfFile = URL.createObjectURL(f);
                        me.fileType = "image/png";
                        me.doLoadImage((s) => {
                            resolve(s);
                        });
                    }).catch(ex => {
                        reject(ex);
                    });
                }
                else {

                    me.doLoadImage((s) => {
                        resolve(s);
                    });
                }

            }
            else {

                me.isPdf = true;
                var loadingTask = window["pdfjsLib"].getDocument(me.urlOfFile);
                var pdf = await loadingTask.promise();
                me.numPages = Number(pdf.numPages);
                me.pdf = pdf;
                await me.doLoadPage(1);
                var pdf = await loadingTask.promise();
                return me;

            }
        } catch (e) {
            if (me._onError) {
                me._onError(e);
            }
            else {
                console.error(e);
            }

           
        }
    }

    getOriginalCanvas() {
        return this._orginalImageCanvas;
    }
    isLocalFile() {
        return this.urlOfFile.indexOf("blob:") == 0;
    }
    getFile() {

        if (!this.isLocalFile()) {
            return this._File;
        }
        else {
            return this._originFile;
        }
    }
    _isOnZoomPhase;
    _orginalImageCanvas;

    _originFile;


    /**
     * Sự kiện on select Region để Edit
     * asyncCallback phải là async function
     * @param {any} asyncCallback
     */
    onSelectPicker(asyncCallback) {
        this._onSelectPicker = asyncCallback;
    }
    _File;
    async getThumbAsFile() {
        var imageData = ui_graph2d.getImage(this.canvas);
        var newImageData = ui_graph2d.scaleImageData(imageData, 0.2);

        return await ui_graph2d.createFileFromImageData(newImageData, "thumbs");

    }
    getZoomValue() {
        return this.zoom;
    }
    _onLoadComplete;
    onLoadComplete(cb) {
        this._onLoadComplete = cb;

    }


    tesseract_recognize_scaleUp = 8;
    getPdfObject() {
        return this.pdf;
    }



    _layers;
    interact;

    detectOnResizePickerEvent;
    currentResizeHandle;
    contextMenuPickerEle;
    contextMenuPickerEvent;

    currentContextMenuContextEvent;
    _onSelectPicker;
    _onAfterEdit;

    _onError;
    _recognizeLanguage = "vie";
    resultWindow;
    resultTextarea;
    fileType;
    isPdf;
    drawEvent;
    deskEle;
    selectorEvent;
    windKeyEvent;



    getScaleValue() {
        return this.zoom;
    }
    getCurrentPageIndex() {
        return this.currentPage;
    }
    zoom = 150;
    //document: HTMLDocument;
    //body: HTMLElement;

    editRegion;
    pageOfPickers = [];
    listOfPickers = [];
    currentPicker;

    numPages = 0;
    history = [];
    trashContainer;

    data;
    urlOfFile;
    pdf;
    canvas;
    ctx;
    currentPage = 1;
    numOfPageRollup = 10;
    //window: Window;

    contextMenuOfSelectRegionRect;

    listOfImageData = [];
    events;
    _onContextMenu;
    /***
     * Bật chế độ vẽ chồng, cho phép vẽ chồng lên một vùng đã được vẽ trước đó.
     * */
    enableOverlayDraw() {
        me._layers.allowOverlay(true);
    }
    disableOverlayDraw() {
        me._layers.allowOverlay(true);
    }
    constructor(ele) {
        var me = this;
        async function start() {
            me.trashContainer = ui_html.createEle("div");
            me.interact = new ui_desk.desk_interact(me);
            me._layers = new ui_desk.desk_layers(me, ele);
            me._layers.drawLayer.disable();
            me._layers.dragLayer.disable();

            me._layers.resizeLayer.disable();
            me._layers.zoomLayer.disable();
            me._layers.drawLayer.onStart(() => {
                if (me.events.handlers[EVENT_RECT_DRAW_BEGIN]) {
                    var ok = me.events.handlers[EVENT_RECT_DRAW_BEGIN]()
                    if (ok) {
                        me.interact.type = ui_desk.desk_interact_emum.draw;
                    }
                }
                else {
                    me.interact.type = ui_desk.desk_interact_emum.draw;
                }
            });
            me._layers.drawLayer.onEnd((R, div) => {
                
                var picker = new ui_rect_picker(
                    R.x,
                    R.y,
                    R.width,
                    R.height
                );
                var ok = true;
                if (me.events.handlers[EVENT_RECT_DRAW_END]) {
                    ok = me.events.handlers[EVENT_RECT_DRAW_END](picker);
                }
                if (!ok) return;
                me._layers.layerBkgEle.appendChild(picker.canvas);

                me.addPicker(picker);
                me._oldCurrentPicker = me.currentPicker;
                me.currentPicker = picker;

                console.log(me._layers);
                
                me._layers.layerBkgEle.click();
                picker.canvas.click();
                me.select(picker);

            });
            me._layers.dragLayer.onEnd((R, picker) => {
                me._layers.layerBkgEle.appendChild(picker);
                me.currentPicker.x = R.x * (100 / me.zoom);
                me.currentPicker.y = R.y * (100 / me.zoom);
                me.currentPicker.drawWithHandle();

                me._raiseOnSelectePicker().then();
            });
            me.events = new EditorEvents();
            me.windKeyEvent = new ui_events.handler(window);


            me._layers.resizeLayer.onStart(() => {
                me.hideContextMenuOfSelecetRegion();
                me._layers.drawLayer.disable();
                me._layers.zoomLayer.disable();
            });
            me._layers.resizeLayer.onReszie((r, ele) => {
                me.currentPicker.x = r.x * 100 / me.zoom;
                me.currentPicker.y = r.y * 100 / me.zoom;
                me.currentPicker.w = r.width * 100 / me.zoom;
                me.currentPicker.h = r.height * 100 / me.zoom;
                me.currentPicker.drawWithHandle();
                me._layers.drawLayer.disable();
                me._layers.zoomLayer.disable();

            });
            me._layers.resizeLayer.onEnd((r, ele) => {
                me.currentPicker.x = r.x * 100 / me.zoom;
                me.currentPicker.y = r.y * 100 / me.zoom;
                me.currentPicker.w = r.width * 100 / me.zoom;
                me.currentPicker.h = r.height * 100 / me.zoom;
                me._layers.layerBkgEle.appendChild(ele);
                me.currentPicker.drawWithHandle();
                //this._layers.drawLayer.enable();
                //this._layers.zoomLayer.enable();
                console.log("this._layers.resizeLayer.onEnd");
                me._raiseOnSelectePicker();
            });
            me._layers.zoomLayer.setConstraint(evt => {
                return evt.ctrlKey;
            });
            me._layers.zoomLayer.onEnd((R, ele) => {
                if (me._asyncOnCtrlSelect) {
                    me._asyncOnCtrlSelect(R, ele, me).then();
                }


            });
            me.detectOnResizePickerEvent = new ui_events.handler(me._layers.layerBkgEle);
            me.detectOnResizePickerEvent.set({
                filter: evt => {
                    return evt.which == 0 && me.currentPicker != undefined;
                },
                onmousemove: evt => {
                    var pos = ui_html.getClientCoordinate(evt, me._layers.layerBkgEle);
                    var resizeHandle = me.currentPicker.detectResizeHandle(pos);
                    me.currentResizeHandle = resizeHandle;
                    if (resizeHandle) {
                        ui_html.setStyle(me._layers.layerBkgEle, {
                            cursor: resizeHandle.cursor
                        });

                    }
                    else {
                        ui_html.setStyle(me._layers.layerBkgEle, {
                            cursor: "default"
                        });
                        me._layers.resizeLayer.disable();
                    }
                }
            });
            new ui_events.handler(me._layers.layerBkgEle).set({
                filter: (evt => { return evt.which == 1 && me.currentResizeHandle != undefined }),
                onmousedown: evt => {
                    me._layers.resizeLayer.startResize(evt, me.currentPicker.canvas, me.currentResizeHandle.cursor);
                    me._layers.dragLayer.disable();
                    me._layers.zoomLayer.disable();

                }
            });
            me.selectorEvent = new ui_events.handler(me._layers.layerBkgEle);
            me.selectorEvent.set({
                filter: (evt) => {

                    return evt.which == 1 && evt.keyCode == undefined && me.currentResizeHandle == undefined;
                },

                onmousemove: evt => {
                    if (me.interact.type != ui_desk.desk_interact_emum.none) {
                        //this._layers.drawLayer.disable();
                    }
                },
                onmouseup: evt => {
                    me._layers.drawLayer.disable();
                    me._layers.dragLayer.disable();
                },
                onmousedown: evt => {
                    me.applyHookKey();
                    if (!evt.ctrlKey) {
                        var canvas = evt.target;
                        var picker = me.findPickerByCanvas(canvas);
                        if (canvas.tagName == "CANVAS" && picker) {

                            me.currentPicker = picker;
                            me.drawAllPickerWithoutHandle();
                            me.currentPicker.drawWithHandle();
                            me.select(me.currentPicker);
                            me._layers.drawLayer.disable();
                            me.hideContextMenuOfSelecetRegion();
                            me._layers.dragLayer.startDrag(evt, me.currentPicker.canvas);
                        }
                        else {

                            me._layers.drawLayer.startDraw(evt);
                            me._layers.dragLayer.disable();
                        }

                    }
                    else {
                        me._layers.drawLayer.disable();
                        me._layers.dragLayer.disable();
                        me._layers.zoomLayer.startDraw(evt);
                    }
                }
            });
            new ui_events.handler(window, {
                onclick: evt => {

                    if (me._layers.layerBkgEle.contains(evt.target)
                        || evt.target == me._layers.layerBkgEle
                        || evt.target == me._layers.ele
                    ) {

                        me.applyHookKey();
                    }
                    else {
                        me.windKeyEvent.unset({ onkeydown })
                    }

                }
            });
        }
        start().then();
    }
    /**
     * Khi người dùng nhấn ctrl và select
     * @param {any} asynCallback
     */
    onCtrlSelect(asynCallback) {
        this._asyncOnCtrlSelect = asynCallback;
    }
    async _raiseOnSelectePicker() {
        if (this.__oldCurrentPicker != this.currentPicker) {
            this.hideContextMenuOfSelecetRegion();
            this.__oldCurrentPicker = this.currentPicker;
        }
        if (this._onSelectPicker) {
            await this._onSelectPicker(this.currentPicker);
        }
    }
    applyHookKey() {
        this.windKeyEvent.set({
            onkeydown: evt => {
                var me = this;
                async function run() {
                    /*
                        Khi người dùng nhấn phím delete thực hiện xóa vùng đang chọn
                        */
                    if (me.events.handlers[EVENT_ON_BEFORE_DELETE_REGION]) {
                        if (await me.events.handlers[EVENT_ON_BEFORE_DELETE_REGION]()) {
                            /*
                             * Nếu vì lý do gì đó mà user chặn xóa
                             * Bỏ qua
                             * **/
                            return;
                        }
                        else {
                            if (me.currentPicker) {
                                me.delete(me.currentPicker);
                            }
                        }
                    }
                    else {
                        if (me.currentPicker) {
                            me.delete(me.currentPicker);
                        }
                    }
                    
                }
                if (evt.keyCode == KEY_DELETE_CODE) {

                    run().then()

                }
               
            }
        });
    }

    createTestPicker() {
        var picker = new ui_rect_picker(
            50, 50, 120, 40

        );

        this._layers.layerBkgEle.appendChild(picker.canvas);

        this.addPicker(picker);
        this.currentPicker = picker;
    }
    getData() {
        
        var ret = [];
        this.pageOfPickers.forEach(p => {
            if (p.pickers.length > 0 && p.pageIndex !== undefined && p.pageIndex > 0) {
                var items = [];
                p.pickers.forEach(r => {
                    var rs = new ui_desk.region_selection()
                    rs.x = r.x;
                    rs.y = r.y;
                    rs.width = r.w;
                    rs.height = r.h;
                    rs.meta = r.meta;
                    items.push(rs);
                });
                var pr = new ui_desk.pageRegion_selection();
                pr.pageIndex = p.pageIndex;
                pr.regions = items;
                ret.push(pr);
            }
        });
        return ret;
    }
    getSelection() {
        return this.currentPicker;
    }


    loadAllPickersToDesk() {

        for (var i = 0; i < this.listOfPickers.length; i++) {
            this.listOfPickers[i].loadTo(this._layers.layerBkgEle);
            //this.listOfPickers[i].drawWithHandle();
            this.listOfPickers[i].drawWithoutHandle();
        }
    }
    loadData(lst) {
        this.clearAllDisplayPickers();
        this.pageOfPickers = [];
        this.currentPage = 1;
        var me = this;
        lst.forEach(P => {
            try {
                var pOP = new ui_desk.page_of_picker();;
                pOP.pageIndex = P.pageIndex;
                pOP.pickers = [];
                P.regions.forEach(r => {

                    var picker = new ui_rect_picker(r.x, r.y, r.width, r.height);
                    picker.desk = me;
                    picker.scaleSize = this.zoom / 100;
                    picker.setData(r);
                    picker.meta = r.meta;

                    pOP.pickers.push(picker);

                });
                me.pageOfPickers.push(pOP);
            } catch (e) {
                console.error(`please call doLoadData like:
                            editor.doLoadData([
                                    {
                                            pageIndex:<number>,
                                            regions:[
                                                    {
                                                      x:<number>,
                                                      x:<number>,
                                                      width:<number>,
                                                      height:<number>
                                                    }
                                                    ]
                                        }

                            ])`)
            }


        });
        if (this.pageOfPickers.length > 0) {
            me.listOfPickers = this.pageOfPickers[0].pickers;
            me.loadAllPickersToDesk();
        }
    }
    //async openFileFromClient() {
    //    debugger;
    //    var me = this;
    //    me.reset();
    //    await me.browseFile();
    //    me.clearAllDisplayPickers();
    //    if (me.isPdf) { // if is pdf file just load the first page
    //        await me.doLoadPage(1);
    //    }
    //    else {
    //        await me.doLoadImage();
    //    }
    //    if (this.events.handlers[EVENT_ON_LOAD_FILE_COMPLETE]) {
    //        await this.events.handlers[EVENT_ON_LOAD_FILE_COMPLETE]();
    //    }
    //}
    async doLoadImage() {
        
        if (!this._orginalImageCanvas) {
            this._orginalImageCanvas = ui_html.createEle("canvas");
        }
        if (this.isLocalFile()) {
            ui_graph2d.loadUrlOfImageToCanvas(this.urlOfFile, this._orginalImageCanvas, 1);
            ui_graph2d.loadUrlOfImageToCanvas(this.urlOfFile, this.canvas, this.zoom / 100);
            this._fixSizeOfEditor();
            return this;
        }
        else {
            var f = await ui_graph2d.createFileFromUrl(this.urlOfFile);
            this._originFile = f;

            ui_graph2d.loadImageFileToCanvas(f, this._orginalImageCanvas, 1);
            ui_graph2d.loadImageFileToCanvas(f, this.canvas, this.zoom / 100);
            this._fixSizeOfEditor();
            return this;


        }

    }
    _fixSizeOfEditor() {
        var R = this.deskEle.getBoundingClientRect();
        ui_html.setStyle(this._layers.layerBkgEle, {
            width: (R.width).toString() + "px",
            height: (R.height).toString() + "px",
        });
        ui_html.setStyle(this._layers.dragLayer._ele, {
            width: (R.width).toString() + "px",
            height: (R.height).toString() + "px",
        });
        ui_html.setStyle(this._layers.drawLayer._ele, {
            width: (R.width).toString() + "px",
            height: (R.height).toString() + "px",
        });
        ui_html.setStyle(this._layers.resizeLayer._ele, {
            width: (R.width).toString() + "px",
            height: (R.height).toString() + "px",
        });
    }
    setContextMenuOfSelectRegion(ele) {
        var me = this;
        new ui_events.handler(window, {
            oncontextmenu: evt => {
                if (me._layers.layerBkgEle.contains(evt.target)
                    || evt.target == me._layers.layerBkgEle
                    || evt.target == me._layers.ele
                    || (me.currentPicker && me.currentPicker.canvas == evt.target)
                ) {
                    evt.stopImmediatePropagation();
                    evt.preventDefault();
                    return true;
                }
            },
            onclick: evt => {

                if (me._layers.layerBkgEle.contains(evt.target)
                    || evt.target == me._layers.layerBkgEle
                    || evt.target == me._layers.ele
                ) {

                    me.applyHookKey();
                }
                else {
                    me.windKeyEvent.unset({ onkeydown })
                }

            }
        });
        ele.oncontextmenu = evt => {
            evt.stopPropagation();
            evt.stopImmediatePropagation();
            evt.preventDefault();
            return true;
        }
        new ui_events.handler(me._layers.layerBkgEle, {
            filter: evt => { return evt.which == 3; },
            onmousedown: evt => {
                var canvas = evt.target;
                var picker = me.findPickerByCanvas(canvas);
                if (picker) {

                    me.currentPicker = picker;
                    me.drawAllPickerWithoutHandle();
                    me.currentPicker.drawWithHandle();
                    
                    var pos = new ui_linear.vector(evt.clientX, evt.clientY);
                    me.showContextMenuOfSelecetRegion(pos);

                }
                evt.stopImmediatePropagation();
                evt.preventDefault();
            }
        });
        ui_html.setStyle(ele, {
            float: "left",
            display: "none",
            position: "absolute"
        });

        me.contextMenuPickerEle = ele;
        me.contextMenuOfSelectRegionRect = ele.getBoundingClientRect();
        new ui_events.handler(ele, {
            filter: evt => {
                return me.currentPicker != undefined;
            },

            onmouseleave: evt => {
                ui_html.setStyle(me.contextMenuPickerEle, {
                    display: "none"
                });
            },
            onmousemove: evt => {
                document.body.appendChild(ele);
                ui_html.setStyle(me.contextMenuPickerEle, {
                    display: "block"
                });
            }
        });
    }
    hideContextMenuOfSelecetRegion() {
        var me = this;
        ui_html.setStyle(me.contextMenuPickerEle, {
            
            display: "none"
           
        });
    }
    showContextMenuOfSelecetRegion(pos) {
        
        var menuRect = ui_html.getRectOfEle(this.contextMenuPickerEle);
        var bodyRect = ui_html.getRectOfEle(window.document.body);
        console.log(menuRect);
        var x2 = menuRect.width + pos.x;
        var y2 = menuRect.height + pos.y;
        if (x2 > bodyRect.x + bodyRect.width) {
            pos.x = bodyRect.x + bodyRect.width - menuRect.width
        }
        if (y2 > bodyRect.y + bodyRect.height) {
            pos.y = bodyRect.y + bodyRect.height - menuRect.height
        }
        ui_html.setStyle(this.contextMenuPickerEle, {
            left: pos.x + 'px',
            top: pos.y + 'px',
            display: "block",
            zIndex: "20000"
        });
    }
    setModeEdit() {
        this.interact.type = ui_desk.desk_interact_emum.edit;
    }
    setModeScale() {
        this.interact.type = ui_desk.desk_interact_emum.scale;
    }
    getCurrentPageOfPicker() {
        for (var i = 0; i < this.pageOfPickers.length; i++) {
            if (this.pageOfPickers[i].pageIndex == this.currentPage) {
                return this.pageOfPickers[i];
            }
        }
    }
    addPicker(picker) {
        var me = this;
        if (!me.listOfPickers) {
            me.listOfPickers = [];
        }
        if (!me.pageOfPickers) {
            me.pageOfPickers = [];
        }
        var currentPageOfPickers = me.getCurrentPageOfPicker();
        if (!currentPageOfPickers) {
            currentPageOfPickers = new ui_desk.page_of_picker();
            currentPageOfPickers.pageIndex = this.currentPage;
            currentPageOfPickers.pickers = me.listOfPickers;
            this.pageOfPickers.push(currentPageOfPickers);
        }

        me.addToHistory(me.listOfPickers);
        me.listOfPickers.push(picker);
        picker.desk = me;
        picker.setScale(me.zoom / 100);
    }
    addToHistory(listOfPickers) {
        var me = this;
        var newLis = [];
        for (var i = 0; i < this.listOfPickers.length; i++) {
            newLis.push(this.listOfPickers[i]);
        }
        me.history.push(newLis);
    }
    delete(picker) {
        console.log(picker);
        var indexOfCurrentPicker = this.listOfPickers.indexOf(picker);
        
        this.addToHistory(this.listOfPickers);
        var newList = [];
        var currentIndex = indexOfCurrentPicker;
        for (var i = 0; i < this.listOfPickers.length; i++) {
            if (this.listOfPickers[i] != picker) {
                newList.push(this.listOfPickers[i]);

            }
            else {
                currentIndex = i;
            }
        }
        this.listOfPickers = newList;
        //this.trashContainer.appendChild(picker.canvas);
        //this.listOfPickers = newList;
        if (currentIndex < this.listOfPickers.length) {
            this.currentPicker = this.listOfPickers[currentIndex];
            this.currentPicker.drawWithHandle();
        }
        else if (currentIndex - 1 < this.listOfPickers.length &&
            currentIndex - 1 >= 0) {
            currentIndex = currentIndex - 1;
            this.currentPicker = this.listOfPickers[currentIndex];
            this.currentPicker.drawWithHandle();
        }
        var currentPageOfPicker = this.getCurrentPageOfPicker();
        if (!currentPageOfPicker) {
            currentPageOfPicker = new pageOfPicker();
            currentPageOfPicker.pageIndex = this.currentPage;

        }
        currentPageOfPicker.pickers = this.listOfPickers;
        picker.canvas.remove();
        
        if (this._layers.drawLayer._ele.childNodes.length == 1) {
            ui_html.setStyle(this._layers.drawLayer._ele.childNodes[0], {
                display: "none"
            });
        }
    }
    async select(picker) {
        if (this.__oldCurrentPicker != this.currentPicker) {
            this.hideContextMenuOfSelecetRegion();
            this.__oldCurrentPicker = this.currentPicker;
        }
        this.drawAllPickerWithoutHandle();
        this.currentPicker = picker;
        this.currentPicker.drawWithHandle();
        if (this._onSelectPicker) {
            await this._onSelectPicker(picker);
        }
    }
    setNumOfPageRollUp(num) {
        this.numOfPageRollup = num;
    }
    unInstallEvents() {
        //var me = this;

        //me.body.onclick = undefined;
        //me.body.onmousedown = undefined;
        //me.body.onmousemove = undefined;
        //me.body.onmouseup = undefined;
    }
    drawAllPickerWithoutHandle() {
        for (var i = 0; i < this.listOfPickers.length; i++) {
            this.listOfPickers[i].drawWithoutHandle();

        }
    }
    findPickerByCanvas(canvas) {
        for (var i = 0; i < this.listOfPickers.length; i++) {
            if (canvas == this.listOfPickers[i].canvas) {
                return this.listOfPickers[i];
            }
        }
    }
    reset() {

        var me = this;
        me.clearAllDisplayPickers();
        me.fileType = undefined;
        me._File = undefined;
        me.currentPicker = undefined;
        me.listOfPickers = [];
        me.pageOfPickers = [];
        if (me.bufferCanvas) {
            Object.keys(me.bufferCanvas).forEach(k => {
                me.bufferCanvas[k].remove();

            });

        }
        me.bufferCanvas = {};
        me.editRegion = undefined;
        me.interact.type = ui_desk.desk_interact_emum.none;

    }
    clear() {
        var me = this;
        me.clearAllDisplayPickers();
        me.fileType = undefined;
        me._File = undefined;
        me._originFile = undefined;
        me.currentPicker = undefined;
        me.listOfPickers = [];
        me.pageOfPickers = [];
        me.editRegion = undefined;
        me.currentPicker = undefined;
        me.interact.type = ui_desk.desk_interact_emum.none;
        me.canvas.getContext("2d").clearRect(0, 0, me.canvas.width, me.canvas.height);
        me._orginalImageCanvas.getContext("2d").clearRect(0, 0, me._orginalImageCanvas.width, me._orginalImageCanvas.height);
    }
    undo() {
        throw "not implement exception"
    }
    clearAllDisplayPickers() {
        var me = this;
        for (var i = 0; i < this.listOfPickers.length; i++) {
            this.trashContainer.appendChild(this.listOfPickers[i].canvas);

        }
    }
    getCurrentRegion() {
        return this.currentPicker;
    }
    async loadFromFile(file) {
        var me = this;
        var _file = file;
        me.urlOfFile = URL.createObjectURL(_file);
        me.fileType = _file.type;
        me._File = file;
        var ret = await me.loadFromUrl(me.urlOfFile, me.fileType);
        if (me.events.handlers[EVENT_ON_LOADING_FILE]) {
            await me.events.handlers[EVENT_ON_LOADING_FILE](100);
        }
        
    }
    async loadFromUrl(urlOfFile, fileType) {
        try {
            var me = this;
            me.reset();
            me.urlOfFile = urlOfFile;
            me.fileType = (fileType == null || fileType == undefined) ? "" : fileType;
            if (me.fileType.indexOf("image/") > -1) {
                me.isPdf = false;

                me.pdf = undefined;
                me.clearAllDisplayPickers();
                if (me.fileType == "image/tiff") {
                    var f = await ui_graph2d.convertTIFToPngFile(me._originFile);
                    me._File = f;
                    me._originFile = f;
                    me.urlOfFile = URL.createObjectURL(f);
                    me.fileType = "image/png";
                    await me.doLoadImage();
                    return {
                        fileName: me._originFile,
                        numPages:1,
                        isPdf: false
                    }
                }
                else {

                    await me.doLoadImage();
                    return {
                        fileName: urlOfFile,
                        numPages: 1,
                        isPdf: false
                    }
                }

            }
            else {

                try {
                    me.isPdf = true;
                    var loadingTask = window["pdfjsLib"].getDocument(me.urlOfFile);
                    var pdf = await loadingTask.promise;
                    me.numPages = Number(pdf.numPages);
                    me.pdf = pdf;
                    await me.doLoadPage(1);
                    me._fixSizeOfEditor();
                    me.clearAllDisplayPickers();
                    me.reset();
                    return {
                        fileName: me.urlOfFile,
                        numPages: me.numPages,
                        isPdf: true
                    }

                } catch (ex) {
                    if (me._onError) {
                        me._onError(ex);
                    }
                    throw ex;
                }

            }
        } catch (e) {
            if (me._onError) {
                me._onError(e);
            }
            else {
                console.error(e);
            }
            
            throw (e);
        }
    }
    getBufferCanvas(pageIndex) {
        return this.bufferCanvas[pageIndex];
    }
    createBufferCanvas(pageIndex) {
        return this.bufferCanvas[pageIndex] = ui_html.createEle("canvas");
    }
    /***
     * Thực hiện browser file trên trình duyệt
     * */
    doBrowserFile() {
        return new Promise(function (resolve, reject) {

            var f = ui_html.createInput("file", {
                display: "none"
            });


            f.setAttribute("accept", "application/pdf,image/*");
            f.onchange = function (evt) {
                resolve(f.files[0])
            }
            f.click();

        });
    }
    async browseFile() {
        if (this.events.handlers[EVENT_ON_LOADING_FILE]) {
            await this.events.handlers[EVENT_ON_LOADING_FILE](0);
        }
        if (this.events.handlers[EVENT_ON_BEFORE_BROWSER_FILE]) {
            if (await this.events.handlers[EVENT_ON_BEFORE_BROWSER_FILE]()) {
                return;
            }
        }
        
        var me = this;
        var file = await this.doBrowserFile();
        if (this.events.handlers[EVENT_ON_LOADING_FILE]) {
            await this.events.handlers[EVENT_ON_LOADING_FILE](1);
        }
        var retInfo = await this.loadFromFile(file);
        if (this.events.handlers[EVENT_ON_LOAD_FILE_COMPLETE]) {
            await this.events.handlers[EVENT_ON_LOAD_FILE_COMPLETE](retInfo);
        }
    }
    async _doLoadAllPage(pageIndex) {
        pageIndex = pageIndex || 1;
        for (var i = 0; i < this.numPages; i++) {
            var retImg = await this.getPageAsImage(pageIndex);
            this.listOfImageData.push(retImg);
            
        }
        

    }
    async doLoadAllPages() {
        var me = this;
        var startPage = 1;
        this.listOfImageData = [];
        ui_html.setStyle(this.deskEle, {
            cursor: "progress"
        });
        await this._doLoadAllPage();
        var H = 0;
        var W = 0;
        this.listOfImageData.forEach(p => {
            H += p.height;
            if (W < p.width) {
                W = p.width
            }
        });
        ui_html.setStyle(this.canvas, {
            width: W.toString() + "px",
            height: H.toString() + "px"
        });
        me.canvas.width = W;
        me.canvas.height = H;
        me.ctx = me.canvas.getContext("2d");
        var y = 0;
        this.listOfImageData.forEach(p => {
            me.ctx.putImageData(p, 0, y);
            y += p.height;
        });
    }

    async doLoadPage(pageNumber) {
        var me = this;
        pageNumber = Number(pageNumber);
        if (pageNumber > me.numPages && me.isPdf)
            return;
        me.currentPage = pageNumber;

        ui_html.setStyle(me.deskEle, {
            cursor: "wait"
        });
        var currentPageOfPickers = me.getCurrentPageOfPicker();
        if (!currentPageOfPickers) {
            currentPageOfPickers = new ui_desk.page_of_picker();
            currentPageOfPickers.pickers = [];
            me.pageOfPickers.push(currentPageOfPickers);
        }
        me.clearAllDisplayPickers();
        me.listOfPickers = currentPageOfPickers.pickers;
        me.loadAllPickersToDesk();
        var imgData = await me.getPageAsImage(pageNumber);
        var R = me.deskEle.getBoundingClientRect();
        
        ui_html.setStyle(me._layers.layerBkgEle, {

            width: Math.ceil(R.width) + "px",
            height: Math.floor(R.height - 8) + "px"
        });

        ui_html.setStyle(me.canvas, {
            width: imgData.width.toString() + "px",
            height: imgData.height.toString() + "px"
        });
        me.canvas.width = imgData.width;
        me.canvas.height = imgData.height;
        me.ctx = me.canvas.getContext("2d");

        me.ctx.clearRect(0, 0, imgData.width, imgData.height);
        me.ctx.putImageData(imgData, 0, 0);
        ui_html.setStyle(
            me.deskEle, {
            cursor: "default"
        });

        if (me._onLoadComplete) {
            me._onLoadComplete(me);
        }
        me._isOnZoomPhase = false;


    }
    async getPageAsImage(pageNumber) {
        var canvas = ui_html.createEle("canvas");
        var ctx = await this.loadPageToCanvas(canvas, pageNumber);
        var imgData = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
        return imgData;
    }
    async loadPageToCanvas(canvas, pageNumber) {
        try {
            var me = this;
            var data = await ui_graph2d.pdfLoadPage(this.pdf, me.zoom / 100, pageNumber, canvas);
            this.ctx = data.canvasContext;
            return data.canvasContext;

        } catch (err) {
            if (this._isOnZoomPhase) return;
            if (me._onError) {
                me._onError(err);
            }
        }

    }
    async doZoom(zoom) {
        this._isOnZoomPhase = true;

        this.zoom = Number(zoom);

        if (this.pdf) {
            await this.doLoadPage(this.currentPage);
            this.doScaleAllPicker();
        }
        else {

            var imgData = ui_graph2d.getImage(this._orginalImageCanvas);

            var newImgData = ui_graph2d.scaleImageData(imgData, this.zoom / 100);


            ui_html.setStyle(this.canvas, {
                width: Math.ceil(newImgData.width) + "px",
                height: Math.ceil(newImgData.height) + "px",

            });
            this.canvas.width = Math.ceil(newImgData.width);
            this.canvas.height = Math.ceil(newImgData.height);
            var ctx = this.canvas.getContext("2d");


            ctx.putImageData(newImgData, 0, 0);

            this.doScaleAllPicker();

        }

    }
    doScaleAllPicker() {
        this.pageOfPickers.forEach(p => {
            p.pickers.forEach(x => {
                x.scale(this.zoom / 100);
            });
        });

        for (var i = 0; i < this.listOfPickers.length; i++) {
            this.listOfPickers[i].clearDraw();
        }
        for (var i = 0; i < this.listOfPickers.length; i++) {
            this.listOfPickers[i].drawWithoutHandle();
        }
        this.currentPicker = undefined;
    }
    async loadThumbs(pageIndex,w, h) {
        
        var me = this;
        
        var retImg = await this.getPageAsImage(pageIndex + 1);
        var scale = w / retImg.width;
        if (retImg.height > retImg.width) {
            scale = h / retImg.height;
        }
        var sImage = ui_graph2d.scaleImageData(retImg, scale);
        var canvas = ui_html.createEle("canvas");
       
        var ctx = canvas.getContext('2d');
       
        canvas.width = retImg.width * scale;
        canvas.height = retImg.height * scale;
        
        ctx.putImageData(sImage, 0, 0);
        var blogUrl = ui_resource.urlFromImageBase64Text(canvas.toDataURL("image/png"));
        
        if (me.events.handlers[EVENT_ON_LOADING_FILE]) {
            
            var percent = 50 + ((pageIndex+1) / this.pdf._pdfInfo.numPages) * 50;
            await me.events.handlers[EVENT_ON_LOADING_FILE](percent);
        }
        return {
            url: blogUrl,
            pageIndex: pageIndex
        };
    }
    setRecognizeLanguage(lang) {
        this._recognizeLanguage = lang;
    }
    onError(cb) {
        this._onError = cb;
    }
    async tesseract_recognize(picker) {
        var me = this;
        var url = await picker.getImageUrl(this.tesseract_recognize_scaleUp);
        var worker = window["Tesseract"].createWorker();
        await worker.load();
        await worker.loadLanguage(me._recognizeLanguage);
        await worker.initialize(me._recognizeLanguage);
        var data = await worker.recognize(url);
        return data;
    }
    createRegion(data, pageNumber) {
        pageNumber = pageNumber || this.currentPage;
        var ret = new ui_rect_picker(data.x, data.y, data.width, data.height);

        ret.scaleSize = 100 / this.zoom;

        ret.setData(data);

        if (pageNumber == this.currentPage) {
            this.addPicker(ret);
            ret.setData(data);
            ret.loadTo(this._layers.layerBkgEle);
            ret.drawWithHandle();
        }

        return ret;
    }
    /**
     * Lất tổng số trang
     * */
    getTotalPages() {
        if (this.pdf && this.pdf._pdfInfo) {
            return this.pdf._pdfInfo.numPages || 0
        }
        return 0;
    }
};
export { ui_pdf_rect_picker }