var  ui_resource = {
    b64toBlob: function (b64Data, contentType, sliceSize) {
        sliceSize = sliceSize || 512;
        const byteCharacters = atob(b64Data);
        const byteArrays = [];

        for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
            const slice = byteCharacters.slice(offset, offset + sliceSize);

            const byteNumbers = new Array(slice.length);
            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }

            const byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }

        const blob = new Blob(byteArrays, { type: contentType });
        return blob;
    },
    urlFromImageBase64Text: function (base64) {
        //'data:image/png;base64,iVB
        var contentType = base64.split(':')[1].split(',')[0];
        var base64Data = base64.split(',')[1];
        const blob = ui_resource.b64toBlob(base64Data, contentType);
        const blobUrl = URL.createObjectURL(blob);
        return blobUrl;
    },
    HTMLImageSetBase64Image: function (ele, base64) {
        if (!ele) {
            console.error("ele was not found");
            return;
        }
        ele.src = ui_resource.urlFromImageBase64Text(base64);
        return ele;
    }
}
export { ui_resource}