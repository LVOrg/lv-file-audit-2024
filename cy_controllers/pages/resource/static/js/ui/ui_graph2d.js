import { ui_html } from "./ui_html.js";
import { ui_workers } from "./ui_workers.js";
function getImage(canvas) {
    var ctx = canvas.getContext("2d");
    var imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    return imgData;
}
function scaleImageData(imageData, ratio) {

    var nW = imageData.width * ratio;
    var nH = imageData.height * ratio;
    var canvas = ui_html.createEle("canvas");
    ui_html.setAttrs(canvas, {
        width: nW.toString(),
        height: nH.toString()
    });
    var destCtx = canvas.getContext("2d");
    var newCanvas = ui_html.createEle("canvas");
    newCanvas.width = Math.max(nW, imageData.width);
    newCanvas.height = Math.max(nH, imageData.height);

    var newContext = newCanvas.getContext("2d");
    newContext.putImageData(imageData, 0, 0);
    imageData = newContext.getImageData(0, 0, Math.max(nW, imageData.width), Math.max(nH, imageData.height));
    destCtx.scale(ratio, ratio);
    destCtx.drawImage(newCanvas, 0, 0);

    return destCtx.getImageData(0, 0, nW, nH);
}
async function resizeImageData(imageData, width, height) {
    const resizeWidth = width >> 0;
    const resizeHeight = height >> 0;
    var ibm = await window.createImageBitmap(imageData, 0, 0, imageData.width, imageData.height, {
        resizeWidth, resizeHeight
    });
    const canvas = document.createElement('canvas')
    canvas.width = resizeWidth
    canvas.height = resizeHeight
    const ctx = canvas.getContext('2d')
    ctx.scale(resizeWidth / imageData.width, resizeHeight / imageData.height)
    ctx.drawImage(ibm, 0, 0);
    return ctx.getImageData(0, 0, resizeWidth, resizeHeight)
}
/**
 * Tạo mới 1 file từ canvas
 * @param {any} canvas
 * @param {any} filename
 */
function createFileFromCanvas(canvas, filename) {
    return new Promise(function (resolve, reject) {
        try {
            var ctx = canvas.getContext("2d");
            canvas.toBlob(blog => {

                var file = new File([blog], filename + ".png", { type: "image/png" })
                resolve(file);
            }, "image/png");
        } catch (e) {
            reject(e);
        }
    })
}
function createFileFromImageData(imageData, fileName) {
    return new Promise(function (resolve, reject){
        try {
            var canvas = ui_html.createEle("canvas");
            canvas.width = imageData.width;
            canvas.height = imageData.height;

            var ctx = canvas.getContext("2d");
            ctx.putImageData(imageData, 0, 0);


            canvas.toBlob(blog => {
                var file = new File([blog], fileName + ".png", { type: "image/png" })
                resolve(file);
            }, "image/png");
        } catch (e) {
            reject(e);
        }
    });


}
function convertTIFToPngFile(file) {
    return new Promise(function (resolve, reject){
        var reader = new FileReader();
        reader.onload = function (e) {
            var arrayBuffer = reader.result;
            var tiff = new window["Tiff"]({ buffer: arrayBuffer });
            var canvas = tiff.toCanvas();
            var items = file.name.split('.');
            var fileName = "";
            for (var i = 0; i < items.length - 1; i++) {
                fileName += items[i] + ".";
            }
            fileName + "png";
            createFileFromCanvas(canvas, fileName).then(f => {
                resolve(f);
            }).catch(e => {
                reject(e);
            });
        }
        reader.onerror = e => {
            reject(e);
        }
        reader.readAsArrayBuffer(file);
    });
}
function grayScale(imgData) {
    return ui_workers.newTask().start(function (task, imgData){
        var pixels = imgData.data;
        for (var i = 0; i < pixels.length; i += 4) {

            var lightness = ((pixels[i] + pixels[i + 1] + pixels[i + 2]) / 3);
            pixels[i] = lightness;
            pixels[i + 1] = lightness;
            pixels[i + 2] = lightness;
        }
        return imgData;

    })(imgData);

}
function contrastImage(imgData, contrast) {
    return ui_workers.newTask().start(function(task, imgData){
        contrast = contrast || 100;
        var d = imgData.data;
        contrast = (contrast / 100) + 1;  //convert to decimal & shift range: [0..2]
        var intercept = 128 * (1 - contrast);
        for (var i = 0; i < d.length; i += 4) {   //r,g,b,a
            d[i] = d[i] * contrast + intercept;
            d[i + 1] = d[i + 1] * contrast + intercept;
            d[i + 2] = d[i + 2] * contrast + intercept;
        }
        return imgData;

    })(imgData);

    //return ui_workers.create<ImageData>((imgData, contrast) => {


    //})(imgData, contrast);

}
function loadImageFileToCanvas(file, canvas, scale){
    scale = scale || 1;
    return loadUrlOfImageToCanvas(URL.createObjectURL(file), canvas, scale);
}
async function createFileFromUrl(url) {
    var res = await fetch(url);
    var mimeType = res.type;
    var blog = await res.blob();
    var file = new File([blog], "tempFile." + mimeType.split('/')[1], { type: mimeType });
    return file;
}
function loadUrlOfImageToCanvas(url, canvas, scale) {
    scale = scale || 1;
    return new Promise(function (resolve, reject) {
        var img = new Image();   // Create new img element
        img.onload = evt => {
            canvas.width = img.width * scale;
            canvas.height = img.height * scale;
            ui_html.setStyle(canvas, {
                width: (img.width * scale).toString() + "px",
                height: (img.height * scale).toString() + "px"
            });
            var ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, img.width * scale, img.height * scale);

            resolve(canvas);
        }
        img.onerror = evt => {
            reject(evt);
        }
        img.src = url;
    })

}
function pdfLoadPage(pdf, scaleRate, pageIndex, canvas) {
    return new Promise(function (resolve, reject) {
        var task = ui_workers.newTask();
        task.start(async function (sender) {
            var page = await pdf.getPage(pageIndex);
            page.cleanupAfterRender = true;
            var scale = scaleRate;
            var viewport = page.getViewport({ scale: scale, });
            ui_html.setStyle(canvas, {
                width: viewport.width + "px",
                height: viewport.height + "px"
            });
            var ctx = canvas.getContext("2d");
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            var renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };
            var pageRendering = page.render(renderContext)
                .promise.then(function () {
                    var r = new ui_graph2d_pdf_info();
                    r.viewPort = new pdf_info_view_port();
                    r.viewPort.scale = scale;
                    r.viewPort.width = viewport.width;
                    r.viewPort.height = viewport.height
                    r.canvasContext = ctx;
                    r.canvas = canvas;
                    r.numPages = Number(pdf.numPages);
                    r.pageIndex = pageIndex;
                    resolve(r);
                }).catch(function(e) {
                    reject(e);
                });
        })();
    });
    

};
function drawRect(ctx, x, y, dx, dy) {

    ctx.moveTo(x, y);
    ctx.lineTo(x + dx, y);
    ctx.lineTo(x + dx, y + dy);
    ctx.lineTo(x, y + dy);
    ctx.lineTo(x, y);
    ctx.stroke();

}
class ui_graph2d_pdf_info  {
    viewPort;
    canvasContext;
    canvas;
    numPages;
    pageIndex;

}
class pdf_info_view_port{
    scale;
    width;
    height;

}
var ui_graph2d = {

    drawRect: drawRect,
    loadUrlOfImageToCanvas: loadUrlOfImageToCanvas,
    pdfInfo: ui_graph2d_pdf_info,
    pdfInfoViewPort: pdf_info_view_port,
    pdfLoadPage: pdfLoadPage,
    getImage: getImage,
    scaleImageData: scaleImageData,
    resizeImageData: resizeImageData,
    createFileFromImageData: createFileFromImageData,
    convertTIFToPngFile: convertTIFToPngFile,
    grayScale: grayScale,
    contrastImage: contrastImage,
    loadImageFileToCanvas: loadImageFileToCanvas,
    createFileFromUrl: createFileFromUrl

};
export { ui_graph2d };