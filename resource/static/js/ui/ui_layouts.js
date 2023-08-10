import { ui_html } from "./ui_html.js";
var ui_layouts = {
    /**
     * make dock full in flex layout
     */
    dockFull: function (ele) {
        ui_html.setStyle(ele, {
            flex: "auto",
            width: "100%",
            height: "100%"
        })

    },
    /**
     * Make debug boder layout
     */
    debugBorder: function (ele) {
        ui_html.setStyle(ele, {
            border: "solid 4px red"
        });

    },
    /**
         * dock element to parent then make layout column
         */
    layoutColumns: function (selector) {
        ui_html.setStyle(selector, {
            display: "flex",
            flexDirection: "column",
            height: "100%"
        });

    },
    layoutRows: function (selector) {
        ui_html.setStyle(selector, {
            display: "flex",
            flexDirection: "row"
        });

    },
    layoutGrid: function (selector, cols, gridGap) {
        gridGap = gridGap || 1;
        var txttemplateCols = "";
        for (var i = 0; i < cols; i++) {
            txttemplateCols += "auto ";
        }
        ui_html.setStyle(selector, {
            display: "grid",
            gridGap: gridGap + "px",
            gridTemplateColumns: txttemplateCols
        });

    },
    layoutGridLoadChildNodes: function (selector, children, cols) {
        var col = 1;
        var row = 1;
        while (children.length > 0) {
            var ele = children[0];
            //ui_html.setStyle(ele, {
            //    gridColumn: "1",

            //});
            selector.appendChild(ele);
            if (col > cols) {
                col = 1;
                row++;
            }
            else {
                col++;
            }
        }

    }
};
export { ui_layouts };