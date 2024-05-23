
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var cloudConsentLogin = await View(import.meta, class CloudConsentLoginView extends BaseScope {


});
export default cloudConsentLogin;