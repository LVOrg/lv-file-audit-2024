
var bs4Module = angular.module("bs4", []);
function addCss(relPath) {
    var items = import.meta.url.split('/');
    var url = import.meta.url.substring(0, import.meta.url.length - items[items.length - 1].length);
    url += relPath;
    $(`<link rel="stylesheet" href="${url}" />`).appendTo("head");
}
addCss("select2.min.css");
import { } from "./select2.full.js";
export default bs4Module;