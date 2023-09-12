import rcmpctModule from "./rcmpt.js"

/**
 Được sử dụng lồng vào bên trong các component mà nó cần template
 */
rcmpctModule.directive("rcmpctJsonViewer", [() => {
    return {
        restrict: "ECA",
        replace: true,
        template:"<div class='json-tree' style='overflow-y:auto'><style>.json-tree li {list-style:none} </style><div id='t'></div></div>",
        link: (s, e, a) => {


            s.$watch(a.source, (n, o) => {
                $(e[0]).find("#t").empty();
                if(n===undefined) return;
                console.log(n);
                var tree = jsonTree.create(n, $(e[0]).find("#t")[0]);
                tree.expand();
            });
        }
    }
}]);
export default rcmpctModule