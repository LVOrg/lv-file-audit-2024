import { module, module_name } from "../js/loader/loaderModule.js";

var header = module.directive("appHeader", function () {
    return {
       
        replace: true,
        template: `<div header >test</div>`
    }
});
console.log(header);
export default header;
