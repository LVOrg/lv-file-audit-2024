var rcpLazyListModule = angular.module("ui", []);
var rcpLazyListDirective = rcpLazyListModule.directive("rcpLazyList", [function () {
    return {
        replace: true,
        template: "<div><div ng-transclude></div></div>",
        transclude:true
    }
    
}]);
export default rcpLazyListModule;