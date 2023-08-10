import bs4Module from "./module.js";
bs4Module.directive("bs4Select", [() => {
    return {
        restrict: "ECA",
        replace: true,
        template: `<div></div>`,
        transclude: true,
        link: (s, e, a) => {
            function reFormat(data, key, value) {
                if (data == undefined || data == null) return [];
                var ret = [];
                data.forEach((item, index) => {
                    var nItem = {};
                    nItem["id"] = item[key];
                    nItem["text"] = item[value];
                    nItem.$dataItem = item;
                    nItem.index = index;
                    ret.push(nItem);
                });
                
                return ret;
            }
            var select = $(e[0]).select2({
                placeholder: a.placeholder,
                allowClear: true,
                quiteMillis:200
            });
            s.$watch(a.ngModel, (n, o) => {

                select.val(n).trigger("change");
            });
            s.$watch(a.source, (n, o) => {
                
                select.select2({
                    data: reFormat(n,a.valueMember||"id",a.displayMember||"text")
                });
            });
            s.$on("$destroy", () => {
                alert("OK");
                select.select2('destroy')
            });
        }
    }
}]);
