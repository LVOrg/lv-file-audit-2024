import { ui_html } from "./ui_html.js";
import { ui_worker } from "./ui_worker";
export default ui_files = {
    fileChunkReader: class {
        _file;
        _chunkSize;
        numOfChunks;
        _offset;
        _reader;
        constructor(file, chunkSize) {
            this._offset = 0;
            this._file = file;
            this._chunkSize = chunkSize;
            this._reader = new FileReader();
            this.numOfChunks = Math.floor(this._file.size / this._chunkSize);
            if (this._file.size % this._chunkSize > 0) {
                this.numOfChunks++;
            }
        }
        read(cb, next) {
            var nextFn = () => {
                if (this._offset < this.numOfChunks) {
                    var blob = this._file.slice(this._offset, this._offset + this._chunkSize);

                    this._reader.onload = evt => {
                        var buffer = evt.target.result;
                        var b = new Blob([new Uint8Array(buffer, 0, buffer.byteLength)]);
                        var data = {
                            blog: b,
                            index: this._offset,
                            length: this.numOfChunks
                        }
                        this._offset++;
                        cb(data, nextFn);
                    }
                    this._reader.readAsArrayBuffer(blob);
                }
            }
            nextFn();
        }
        readAsFile(cb, next) {
            var me = this;
            var fileExtentsion = "";
            var fileNameOnly = this._file.name;
            if (me._file.name.indexOf('.') > -1) {
                fileExtentsion = me._file.name.split('.')[me._file.name.split('.').length - 1];
                fileNameOnly = fileNameOnly.substring(0, fileNameOnly.length - fileExtentsion.length - 1);
            }
            this.read((data, next) => {

                var _data = {
                    file: new File([data.blog], fileNameOnly + "[" + data.index + "]." + fileExtentsion, {
                        type: me._file.type

                    }),
                    index: data.index,
                    length: data.length
                };
                cb(_data, next);
            });
        }
    },
    browserFile: function (accept) {
        return new Promise(Function(resolve, reject){
            accept = accept || "*";
            var f = q.html.createEle("input");
            f.setAttribute("type", "file");
            f.setAttribute("accept", accept);
            f.onerror = evt => {
                reject(evt);
            };
            f.onchange = evt => {
                resolve(f["files"][0]);
            }
            f.click();
        });
    },
    browserFiles: function (accept) {
        return new Promise(function (resolve, reject) {
            accept = accept || "*";
            var f = ui_html.createEle("input");
            f.setAttribute("type", "file");
            f.setAttribute("accept", accept);
            f.setAttribute("multiple", 'multiple');
            f.onerror = evt => {
                reject(evt);
            };
            f.onchange = evt => {
                resolve(f["files"]);
            }
            f.click();
        });
    },
    readChunk: function (file, chunkSize) {
        return new fileChunkReader(file, chunkSize);
    },
    ziptor: class {
        _zip;
        constructor() {
            this._zip = new window["JSZip"]();
        }
        addFile(file) {
            var me = this;
            return new Promise(function (resolve, reject) {

                try {
                    readChunk(file, file.size).read((data, next) => {
                        me._zip.file(file.name, data.blog);
                        next();
                        resolve(me);
                    });
                } catch (e) {
                    reject(e);
                }
            });

        }
        generateAsFile(){
            var me = this;
            return new Promise(function (resolve, reject) {
                ui_worker.newTask().startAsync((sender, done, err) => {
                    me._zip.generateAsync({ type: "uint8array" }).then((f) => {
                        var b = new Blob([f]);
                        var _f = new File([b], "new.zip", {
                            type: "application/zip"
                        });
                        done({
                            sender: me,
                            file: _f
                        });
                    });
                })().then((r) => {
                    resolve(r);
                }).catch(ex => {
                    reject(ex);
                });
            });

        }
    },
    createZip: function () {
        return new ui_files.ziptor();
    }
}