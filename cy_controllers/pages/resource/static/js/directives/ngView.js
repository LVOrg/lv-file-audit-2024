
import { module, module_name } from "./../loader/loaderModule.js";
import qViews from "./../loader/views.js";
var ngModule = module;
var qNgView= ngModule.directive("qNgView", () => {
    return {
        restrict: "ECA",
        template: "<div></div>",
        replace: true,
        link: function (s, e, a) {
           
            var Params = s.$eval(a.params);
            a.$observe("resource", v => {
                qViews.loadViewFromNgScope(s, Params, v).then(result => {
                    var oldScope = angular.element(e.children()[0]).scope();
                    if (oldScope) {
                        oldScope.$destroy();
                    }
                    $(e[0]).empty()
                    result.scope.$element.appendTo(e[0]);
                    var comment = document.createComment(`this content load from ${v}`);
                    var commentSuggest = document.createComment(`suggest: use inherit from url of Ancestor in ${v} then set "body" attribute, region-parent and region at ancestor will make more complex view`);
                    $(comment).insertBefore(e.children()[0]);
                    $(commentSuggest).appendTo(e[0]);
                }).catch(ex => {
                    console.error(ex);
                });
            });
        }
    }
});
export default qNgView;