import utils from "./utils.js";
import { postId } from "../ui/core.js"
window.___sync___ = function (id,classObj) {
    qViews.reSync(id, classObj);
}

var qViews = {
    qModuleName: "q-ng",
    readyObserve: class {
        constructor(ele, cb) {
            function R() {
                var r = ele.getBoundingClientRect();
                if (r.width > 0 && r.height > 0) {
                    cb();
                }
                else {
                    setTimeout(() => { R(); }, 10);
                }
            }
            R();
        }
    },
    sizeObserve: class {

        ele;
        rect;
        _onChange;
        _timer;
        constructor(ele) {
            this.ele = ele;
            $(this.ele).css({
                "overflow": "hidden"
            });
            this.rect = this.ele.getBoundingClientRect();
            this._run();
        }
        onChange(cb) {
            this._onChange.push(cb);
        }
        destroy() {
            clearInterval(this._timer);
            this._onChange = [];
        }
        fireOnChange() {
            var me = this;
            me._onChange.forEach(f => {
                if (me.rect.width > 0 && me.rect.height > 0) {
                    f(me.rect);
                }
            });
        }
        _run() {
            var me = this;
            function r() {
                var rect = me.ele.getBoundingClientRect();
                if ((rect.width > 0 && rect.height > 0) &&
                    (rect.width != me.rect.width ||
                        rect.height != me.rect.height)) {
                    me._onChange.forEach(f => {
                        f(rect);
                    });
                    me.rect = rect;
                }
                setTimeout(r, 200);
            }
            r();
        }
    },
    XSCOPE_READY: class {
        __onReady__ = []
        $onReady(cb) {
            this.__onReady__.push(cb);
        }
        __fireOnReady__() {
            this.__onReady__.forEach(f => {
                f();
            });
        }
    },
    XSCOPE: class {
        $viewId;
        $parent;
        $root;

        constructor() {

        }
        $getViewId() {
            if (this.$root == this) return;
            if (this.$viewId) {
                return this.$viewId;
            }
            else {
                var parent = this.$parent;
                while (parent !== this.$root) {
                    if (parent["$viewId"]) {
                        return parent.$viewId;
                    }
                    else {
                        parent = parent.$parent;
                    }
                }
            }
        }
        async $loadView(url, args) {
            return await qViews.loadViewFromNgScope(this, args, url);
        }
        $getWindow(id) {
            this["$windows"] = this["$windows"] || {};
            return this["$windows"][id];
        }

        $findEle(selector) {
            return new Promise(function (resolve, reject) {
                var me = this;
                function watch(cb) {
                    if (me["$element"] && $.contains($('body')[0], me["$element"].find(selector)[0])) {
                        resolve(me["$element"].find(selector))
                    }
                    else {
                        setTimeout(() => {
                            watch(cb);
                        }, 10)
                    }
                }
                watch(cb);
            });
        }

    },
    _onReady: function (root) { },
    onReady: function (cb) {
        qViews._onReady = cb;
    },
    _onBeforeLoadViewHandlers: [],
    _onAfterLoadViewhandlers: [],
    beforeLoadViewSender: class {
        view;
        _index;
        done;

    },
    onBeforeLoadView: function (cb) {
        qViews._onBeforeLoadViewHandlers.push(cb);
    },
    onAfterLoadView: function (cb) {
        qViews._onAfterLoadViewhandlers.push(cb);
    },
    raiseOnBeforeLoadView: function (sender, next) {
        sender.done = function () {
            sender._index++;
            if (sender._index < _onBeforeLoadViewHandlers.length) {
                qViews.raiseOnBeforeLoadView(sender, sender._index);
            }
            else {
                next();
            }
        }
        if (sender._index < qViews._onBeforeLoadViewHandlers.length) {
            qViews._onBeforeLoadViewHandlers[sender._index](sender);
        }
        else {
            next();
        }
    },
    raiseOnAfterLoadView: function (sender, next) {
        sender.done = function () {
            sender._index++;
            if (sender._index < qViews._onAfterLoadViewhandlers.length) {
                qViews.raiseOnAfterLoadView(sender, sender._index);
            }
            else {
                next();
            }
        }
        if (sender._index < qViews._onAfterLoadViewhandlers.length) {
            qViews._onAfterLoadViewhandlers[sender._index](sender);
        }
        else {
            next();
        }
    },
    scriptCompileInfo: class scriptCompileInfo {
        Fn;
        injections;

    },
    ngView: class {
        ownerScope;
        scope;
        display;
        element;

    },

    combineWithParent: function combineWithParent(view) {
        var parent = view.parentView;

        var eleContent = undefined;
        var bodyEle = undefined;
        var ele = undefined;
        var rootEle = undefined;

        var views = [];
        while (parent) {
            views.push(parent);
            parent = parent.parentView;
        }


        parent = views.pop();
        while (parent) {
            ele = $('<div>' + parent.content + '</div>').children()[0];
            var comment = $(document.createComment(`begin inherit load from ${parent.url}`));
            comment.insertBefore($($(ele).contents()[0]));
            var endComment = $(document.createComment(`end inherit load`));
            if (!rootEle) {
                rootEle = ele;
            }
            if (bodyEle) {

                endComment.appendTo(ele);

                bodyEle.replaceWith($(ele).contents());
            }


            bodyEle = $(rootEle).find('[body]');
            parent = views.pop();
        }

        ele = $('<div>' + view.content + '</div>').children()[0];

        var parentRegions = $(ele).find("[region-parent]");
        parentRegions.each((index, p) => {
            var name = $(p).attr("region-parent");
            var x = $(rootEle).find("[region='" + name + "']");
            var comment = $(document.createComment(`overwerite to ${name}`));
            comment.insertBefore($(p).contents()[0]);
            var endComment = $(document.createComment(`end overwerite`));
            endComment.appendTo(p);
            x.replaceWith($(p).contents());
        });
        if (bodyEle) {
            var comment = $(document.createComment(`begin inherit load from ${view.url}`));
            comment.insertBefore($($(ele).contents()[0]));
            var endComment = $(document.createComment(`end inherit load`));
            endComment.appendTo(ele);
            bodyEle.replaceWith($(ele).contents());
            view.content = rootEle.outerHTML;
        }


    },
    loadViewFromNgScope: async function (scope, Params, url) {
        if (!scope.$$urlInfo) {

            scope.$$urlInfo = utils.createUrlInfo('');
        }
        var _url = url;
        if (!utils.isAbsUrl(_url)) {
            _url = scope.$$urlInfo.absUrl.ref + '/' + url;
        }
        var res = await utils.loadView(_url);
        utils.reduceView(res);
        var parent = res.parentView;
        while (parent) {
            utils.reduceView(parent);

            parent = parent.parentView;
        }
        qViews.combineWithParent(res);
        var result = await utils.reduceViewWithUrlOfScript(res);

        result.ownerScope = scope;
        var views = [];
        views.push(result);
        var parent = result.parentView;
        while (parent != null) {
            views.push(parent);
            parent = parent.parentView;
        }

        var cView = views.pop();
        while (cView) {
            cView.ownerScope = scope;
            
            await qViews.compileView(cView, Params);
            var cView = views.pop();
        }

        if (result.scope.$element) {
            result.scope.$viewId = result.scope.$element.attr("view-id");
        }

        var sender = new qViews.beforeLoadViewSender();
        sender._index = 0;
        sender.view = result;
        var retObj = await new Promise(function (resolve, reject) {
            qViews.raiseOnBeforeLoadView(sender, function () {
                function watch(cb) {

                    var isOk = result.scope.$element.hasClass("ng-scope");
                    if (isOk) {
                        cb();
                    }
                    else {
                        setTimeout(() => {
                            watch(cb);
                        }, 1);
                    }
                }
                watch(function () {
                    result.scope.$element.css({
                        display: result.display
                    });
                    sender._index = 0;
                    qViews.raiseOnAfterLoadView(sender, function () {
                        resolve(result);
                    });

                });
            });
        });
        return retObj;
    },
    compileScript: function compileScript(scriptContent) {
        console.log("Very important");
        var ret = new qViews.scriptCompileInfo();
        

        var t = eval(scriptContent);
        if (angular.isArray(t)) {
            ret.injections = [];
            for (var i = 0; i < t.length - 1; i++) {
                try {
                    ret.injections.push(q.ng.getService(t[i]));
                } catch (e) {
                    console.error(e);
                }
            }
            ret.Fn = t[t.length - 1];
            ret;
        }
        else if (angular.isFunction(t)) {
            ret.Fn = t;
            ret.injections = [];
        }
        return ret;
    },
    hash: {},
    reSync: function (id, classScope) {
        function run(id, classScope) {
            var me = this;
            function w() {
                var eles = $("body").find(`[fake-ui-id="${id}"]`);
                if (eles.length == 0)
                    setTimeout(w, 10);
                else
                    qViews.hash[id] = {
                        classScope: classScope,
                        template: $(eles[0])
                    };

            }
            w();
        }
        new run(id, classScope)
    },
    watchSync: function(id,callback) {
        function run(id, callback) {
            var me = this;
            function w() {
                if (!qViews.hash[id])
                    setTimeout(w, 10);
                else
                    callback(qViews.hash[id]);

            }
            w();
        }
        new run(id, callback)
    },
    compileView: function (view, Params) {
        var url = URL.createObjectURL(new Blob([view.url]));
        var id = url.split('/')[url.split('/').length - 1];
        var viewEle = $($("<div>" + view.content + "</div>").children()[0]);;

        viewEle.attr("fake-ui-id", id);
        var scriptsEles = viewEle.find("script[type='module']");
        
        

        if (scriptsEles.length > 0) {
            //scriptsEles.each((i, e) => {
            //    $(e).attr("ui-id", id);
            //    $(e).appendTo("head");
            //});
            var content = $(scriptsEles[scriptsEles.length - 1]).text();
           
            //export default 
            var exportPosition = content.indexOf("\nexport ");
            if (exportPosition == -1)
                exportPosition = content.indexOf("export ");
            var defaultPosition = content.indexOf("default ", exportPosition + 1);
            var classPosition = content.indexOf(" ", defaultPosition + 1);
            var classPositionEnd = content.indexOf(" ", classPosition + 1);
            var className = content.substring(classPosition, classPositionEnd);
            while (className.indexOf(";")>-1)
                className = className.replace(";", "");
            
            var txtExtens = `\n${className}.prototype.__set_ui_id__=function(id){
                                     ${className}.prototype.__ui_id__=id;   
                             };`

            
            $(scriptsEles[scriptsEles.length - 1]).text(content);
            content += txtExtens;
            content += `;window.___sync___('${id}',${className})`;
            $(scriptsEles[scriptsEles.length - 1]).text(content);
            viewEle.appendTo("body");
            view.scope = view.ownerScope.$new(true);
            view.scope.$element = viewEle;
            view.element = viewEle;
            if (view.scope.$element[0]) {
                view.display = view.scope.$element[0].style.display
            }
            //view.scope.$element.css({
            //    display: "none"
            //});
            return new Promise(function (resolve, reject) {
                qViews.watchSync(id, function (sender) {

                    var childScope = new sender.classScope();
                    view.scope = utils.combine(view.scope, sender.classScope);
                    var $compile = utils.getService("$compile");
                    $compile(view.scope.$element)(view.scope);
                    view.scope.$digest();
                    
                    resolve(view);
                });
            });
            
        }
        console.log(viewEle[0]);
        view.scope = view.ownerScope.$new(true);

        view.scope.$element = $($("<div>" + view.content + "</div>").children()[0]);
        view.element = viewEle;
        if (view.scope.$element[0]) {
            view.display = view.scope.$element[0].style.display
        }
        view.scope.$element.css({
            display: "none"
        });
        
        return new Promise(function (resolve, reject) {
            view.scope.$element.appendTo("body");
            view.scope.$$url = view.url.split("?")[0];

            view.scope.$$urlInfo = utils.createUrlInfo(view.url);
            var $compile = utils.getService("$compile");

            $compile(view.scope.$element)(view.scope);
            (view.preSscripts || []).forEach(s => {
                var script = compileScript(s);
                if (!script.injections) script.injections = [];
                if (script.injections.length == 0 && script.Fn) {

                    script.Fn(view.scope, Params);
                }
                else {
                    var objArray = [];
                    script.injections.forEach(o => {
                        objArray.push(o);
                    });
                    objArray.push(view.scope);
                    if (!angular.isArray(Params)) {
                        Params = [Params];
                    }
                    if (Params && Params.length) {
                        for (var i = 0; i < Params.length; i++) {
                            objArray.push(Params[i]);
                        }
                    }
                    if (script.Fn)
                        script.Fn.apply(this, objArray);
                }
            });
            view.inlineScripts.forEach(s => {
                var script = qViews.compileScript(s);
                if (script.injections.length == 0) {
                    script.Fn(view.scope, Params);
                }
                else {
                    var objArray = [];
                    script.injections.forEach(o => {
                        objArray.push(o);
                    });
                    if (!angular.isArray(Params)) {
                        Params = [Params];
                    }
                    if (Params && Params.length) {
                        for (var i = 0; i < Params.length; i++) {
                            objArray.push(Params[i]);
                        }
                    }
                    objArray.push(view.scope);
                    script.Fn.apply(this, objArray);
                }
            });
            console.log("XSCOPE_READY combine", view.scope["__onReady__"]);
            postId(view, id, function () {
                resolve(view);
            });
           
        });
        
    },
    createWindow: async function (url, args, s) {
        s = s || angular.element("body").scope().$root;
        var $compile = utils.getService("$compile");
        var w = new q.UiDesk.WINDOW();
        var _url = url + "?t=" + (new Date()).getTime();
        var view = await qViews.loadViewFromNgScope(s, args, _url);
        var R = view.scope.$element[0].getBoundingClientRect();
        var attr = view.element.attr('title');
        if (typeof attr !== 'undefined' && attr !== false) {
            var titleEle = $("<span>" + view.element.attr("title") + "</span>");
            $compile(titleEle)(view.scope);
            w.setTitleEle(titleEle[0]);
        }

        w.setBody(view.scope.$element[0]);
        w.onShow(() => {
            view.scope.$element.find("input").focus();
        });
        var footer = view.scope.$element.find("footer");
        if (footer.length > 0) {
            w.setFooter(footer[0]);
        }
        view.scope.$element = $(w.getEle());
        view.scope.$doClose = () => {
            w.hide();
        };
        w["scope"] = view.scope;
        resolve(w);
    },
    createDialog: async function (url, args, s) {
        s = s || angular.element("body").scope().$root;
        var $compile = utils.getService("$compile");
        var w = new q.UiDesk.DIALOG();
        var _url = url + "?t=" + (new Date()).getTime();
        var view = await qViews.loadViewFromNgScope(s, args, _url);
        var R = view.scope.$element[0].getBoundingClientRect();
        var attr = view.element.attr('title');
        if (typeof attr !== 'undefined' && attr !== false) {
            var titleEle = $("<span>" + view.element.attr("title") + "</span>");
            $compile(titleEle)(view.scope);
            w.setTitleEle(titleEle[0]);
        }

        w.setBody(view.scope.$element[0]);
        w.onShow(() => {
            view.scope.$element.find("input").focus();
        });
        var footer = view.scope.$element.find("footer");
        if (footer.length > 0) {
            w.setFooter(footer[0]);
        }
        view.scope.$element = $(w.getEle());
        view.scope.$doClose = () => {
            w.hide();
        };
        w["scope"] = view.scope;
        return w;
    },
    compile: function (ele, scope) {

        return new Promise(function (resolve, reject) {
            function W() {
                if ($(ele).hasClass("ng-scope")) {
                    resolve(ele)
                }
                else {
                    setTimeout(W, 10);
                }
            }
            W();
            var $compile = utils.getService("$compile");
            $compile($(ele))(scope);
            scope.$applyAsync();
        });
    },

    watchNg: function () {
        var scope = angular.element("body").scope();
        if (scope) {

            var r = scope;
            r.$root.$$urlInfo = q.utils.createUrlInfo(window.location.pathname);
            scope["$$urlInfo"] = q.utils.createUrlInfo(window.location.pathname);
            scope = q.utils.combine(scope, new XSCOPE());
            scope.$root = q.utils.combine(scope.$root, new XSCOPE());
            if (_onReady) {

                _onReady(r.$root);
            }
        }
        else {
            setTimeout(watchNg, 1);
        }
    }
}
export default qViews;