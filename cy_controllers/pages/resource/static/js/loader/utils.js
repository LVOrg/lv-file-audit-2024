var  utils= {
    __utils__ : {
        hasStart: false
    },
    isUrlOfPage:function(url) {
        var detect = false;
        var i = url.length - 1;
        while ((!detect) && (i > 0)) {
            detect = url[i] === '.';
            if (detect) return detect;
            i--;
        }
        return detect;
    },
    travelToParent:function (url){
        if (utils.isUrlOfPage(url)) {
            var page = url.split('/')[url.split('/').length - 1];
            url = url.substring(0, url.length - page.length - 1);
        }
        return url;
    },
    loadContentFromUrl: function (url) {
        return new Promise(function (resole, reject) {
            fetch(url).then(function (response) {
                return response.text();
            }).then((html) => {
                resole({

                    isRedirect: false,
                    responseText: html

                });
            })
                .catch(function (error) {
                    reject(error);
                });
        });
    },
    loadListOfContentFromListOfUrls:async function(urls){
        var contents = [];
        for (var i = 0; i < urls.length; i++) {
            var res = await utils.loadContentFromUrl(urls[i]);
            if (res.isRedirect)
                window.location.href = res.url;
            else
                contents.push(res.responseText);
        }
        return contents;
    },
    loadView:async function loadView(_url) {
        var url = _url;
        if (window.location.href.indexOf("?") > -1)
            url = url + "?" + window.location.href.split("?")[1].split("#")[0];
        if (window.location.href.indexOf("#") > -1)
            url = url + "?" + window.location.href.split("#")[1];
        var res = await utils.loadContentFromUrl(url);

        if (res.isRedirect) {
            window.location.href = res.url;
            return;
        }
        var ret = {

            inheritPapes:[]
        };
        ret.originContent = res.responseText;
        var ele = $("<div>" + ret.originContent + "</div>");

        ret.url = url;
        ret.parentUrl = utils.travelToParent(url);
        ele.find('link[rel="stylesheet"]').each((index, l) => {
            var href = $(l).attr("href");
            if (href) {
                if (!utils.isAbsUrl(href)) {
                    href = ret.parentUrl + '/' + href;
                    $(l).attr("href", href);
                }
            }

        });
        ret.originContent = ele.html();
        if ($(ele.children()[0]).attr("inherit")) {

            var inheritPage = $(ele.children()[0]).attr("inherit");
            if (!utils.isAbsUrl(inheritPage)) {
                inheritPage = trimStartCharater(inheritPage, '/');
                inheritPage = ret.parentUrl + '/' + inheritPage;
            }
            ret.inheritPapes.push(inheritPage);
            ret.parentView = await loadView(inheritPage);
            return ret;
        }
        else {
            return ret;
        }
    },
    reduceView:function reduceView(view) {
        var url = view.url;
        var content = view.originContent;
        if (this.isUrlOfPage(url)) {
            var page = url.split('/')[url.split('/').length - 1];
            url = url.substring(0, url.length - page.length - 1);
        }
        var rScript = /(\<script\s\s*src\s*\=\s*('|").+('|")\s*\>\s*\<\/script\>|\<script>(\n)*.+(\n)*\<\/script\>)/;
        var rInline = /\<script\s+src\=(\'|\")(.)*\>/;

        if (content.indexOf("<body>") > -1) {
            var x = content.indexOf("<body>") + "<body>".length;
            var y = content.indexOf("</body>", x);
            content = content.substring(x, y);
        }
        var ret = [];

        var r = rScript.exec(content);
        while (r != null) {
            var startIndex = r.index;

            var endIndex = content.indexOf("</script>", startIndex + 1) + "</script>".length;
            var scriptContent = content.substring(startIndex, endIndex);
            var isInline = rInline.exec(scriptContent);
            if (isInline) {

                var scriptSource = scriptContent;
                if (scriptSource.indexOf("'") > -1) {
                    scriptSource = scriptSource.split("'")[1].split("'")[0];
                }
                if (scriptSource.indexOf('"') > -1) {
                    scriptSource = scriptSource.split('"')[1].split('"')[0];
                }
                r = rScript.exec(content);
                var urlRoot = "";
                var items = url.split('/');
                for (var i = 0; i < items.length - 1; i++) {
                    if (items[i] !== "") {
                        urlRoot += items[i] + "/";
                    }
                }

                var detect = false;
                var i = url.length - 1;
                while ((!detect) && (i > 0)) {
                    detect = url[i] === '.';
                    if (detect) break;
                    i--;
                }
                if (!detect) {
                    if (url.toLowerCase().indexOf((window.location.protocol + "//" + window.location.host).toLowerCase()) === -1) {
                        urlRoot += '/' + url;
                    }
                }
                while (urlRoot.substring(0, 1) == "/") {
                    urlRoot = urlRoot.substring(1, urlRoot.length);
                }

                scriptSource = scriptSource.replace("~/", "");
                if (scriptSource.toLowerCase().indexOf((window.location.protocol + "//" + window.location.host).toLowerCase()) === -1) {
                    var scriptUrl = urlRoot;
                    if (!detect) {
                        scriptUrl = urlRoot + '/' + scriptSource;
                    }

                    if (scriptUrl.indexOf("://") > -1) {
                        items = scriptUrl.split("://");
                        scriptUrl = items[1];
                        while (scriptUrl.indexOf("//") > -1) {
                            scriptUrl = scriptUrl.replace("//", "/");
                        }
                        scriptUrl = items[0] + "://" + scriptUrl;
                    }
                    else {
                        if (url.toLowerCase().indexOf((window.location.protocol + "//" + window.location.host).toLowerCase()) === -1) {
                            scriptUrl = window.location.protocol + "//" + window.location.host + "/" + scriptUrl;
                        }
                        else {
                            if (url.substring(url.length - 5, url.length).toLowerCase() === ".html") {
                                var page = url.split('/')[url.split('/').length - 1];
                                scriptUrl = url.substring(0, url.length - page.length) + scriptSource;
                            }
                            else {

                                scriptUrl = url + '/' + scriptSource;
                            }
                        }
                    }
                    ret.push({ url: scriptUrl });
                }
                else {
                    ret.push({ url: scriptSource });
                }
                content = content.replace(r[0], "");
            }
            else {


                ret.push({ scriptContent: scriptContent.replace("<script>", "").replace("</script>", "") });
                content = content.replace(scriptContent, "");
            }

            r = rScript.exec(content);

        }
        var inlineScripts = [];
        var inlineSrciptIndex = content.indexOf("<script>");
        while (inlineSrciptIndex > -1) {
            var startReplace = inlineSrciptIndex;
            inlineSrciptIndex += "<script>".length;
            var endIndexInlineScript = content.indexOf("</script>", inlineSrciptIndex);
            var endReplace = endIndexInlineScript + "</script>".length;
            if (endIndexInlineScript > -1) {
                var strScriptContent = content.substring(inlineSrciptIndex, endIndexInlineScript);
                inlineScripts.push(strScriptContent);
                content = content.substring(0, startReplace) + content.substring(endReplace, content.length);
            }
            inlineSrciptIndex = content.indexOf("<script>");
        }


        view.content = content;
        view.scriptUrls = [];
        ret.forEach(r => {
            view.scriptUrls.push(r.url);
        });
        view.inlineScripts = inlineScripts;
        return view;
    },
    reduceViewWithUrlOfScript: async function (view) {
        view.preSscripts = await utils.loadListOfContentFromListOfUrls(view.scriptUrls);
        return view;
    },
    absolutePath:function (base, relative) {
        var stack = base.split("/"),
            parts = relative.split("/");
        stack.pop(); // remove current file name (or empty string)
        // (omit if "base" is the current folder without trailing slash)
        for (var i = 0; i < parts.length; i++) {
            if (parts[i] == ".")
                continue;
            if (parts[i] == "..")
                stack.pop();
            else
                stack.push(parts[i]);
        }
        return stack.join("/");
    },
    convertToAbsUrl: function (path) {
        var index = path.indexOf("/../");
        if (index > -1) {
            return absolutePath(path.substring(0, index), path.substring(index, path.length))
        }
        else {
            return path;
        }
    },
    createUrlInfo: function (url) {
        utils.__utils__.hasStart = true;
        function fix(txt) {
            while (txt[txt.length - 1] == '/') {
                txt = txt.substring(0, txt.length - 1)
            }
            return txt;
        }
        function isUrlOfPage(currentUrl) {
            var detect = false;
            var i = currentUrl.length - 1;
            while ((!detect) && (i > 0)) {
                detect = currentUrl.substring[i] === '.';
                if (detect) return detect;
                i--;
            }
            return detect;
        }
        if (url.indexOf(window.location.protocol + "//" + window.location.host) == 0) {
            var prefix = window.location.protocol + "//" + window.location.host
            url = url.substring(prefix.length, url.length)
        }
        url = url.split('?')[0];

        url = utils.convertToAbsUrl(url);

        while (url.substring(url.length - 1, url.length) === "/") {
            url = url.substring(0, url.length - 1);
        }
        if (url.indexOf(".html") > -1) {
            url = url.substring(0, url.indexOf(".html"));
            var items = url.split("/");
            url = "";
            for (var i = 0; i < items.length - 1; i++) {
                if (items[i] !== "") {
                    url += items[i] + "/";
                }
            }
            url = url.substring(0, url.length - 1);
            if (window.location.protocol + "//" + window.location.host === url) {
                var ret = {
                    relUrl: {},
                    absUrl: {}
                };
                ret.host = window.location.protocol + "//" + window.location.host;
                
                ret.relUrl.ref = "";
                ret.value = "";
                
                ret.absUrl.ref = url;
                ret.absUrl.value = url;
                return ret;

            }
            else {
                var root = window.location.protocol + "//" + window.location.host;
                var fullUrl = root + '/' + url + "/" + items[items.length - 1] + ".html";
                var fullRef = root + '/' + url;
                var retInfo = {
                    relUrl: {},
                    absUrl: {}
                };
                retInfo.host = root;
                
                retInfo.relUrl.ref = fix(url);
                retInfo.value = fullUrl.substring(root.length, fullUrl.length);
                
                retInfo.absUrl.ref = fullRef;
                retInfo.absUrl.value = fullUrl;
                return retInfo;
            }
        }
        if (window.location.protocol + "//" + window.location.host === url) {
            var retInfo = {
                relUrl: {},
                absUrl: {}
            };
            retInfo.host = window.location.protocol + "//" + window.location.host;
            retInfo.relUrl.ref = "";
            retInfo.relUrl.value = "";
            retInfo.absUrl.ref = fix(url);
            retInfo.absUrl.value = url;
            return retInfo;
        }
        else if (!utils.__utils__.hasStart) {

            var root = window.location.protocol + "//" + window.location.host;
            var fullUrl = url;
            var retInfo = {
                relUrl: {},
                absUrl: {}
            };
            retInfo.host = root;
            retInfo.relUrl.ref = fix(url.substring(root.length, url.length));
            retInfo.relUrl.value = fullUrl.substring(root.length, fullUrl.length);
            retInfo.absUrl.ref = fix(url);
            retInfo.absUrl.value = fullUrl;

            return retInfo;
        }
        var ret = {
            relUrl: {},
            absUrl: {}
        };
        ret.host = window.location.protocol + "//" + window.location.host;
        ret.relUrl.ref = "";
        ret.relUrl.value = "";
        ret.absUrl.value = "";
        ret.absUrl.ref = "";


        if (url.length > ret.host.length) {
            if (url.substring(0, ret.host.length).toLowerCase() === ret.host.toLowerCase()) {
                url = url.substring(ret.host.length + 1, url.length);
            }
        }
        var prefix = url.split('?')[0].split("://")[0];
        var tail = url.split('?')[0].split("://")[1];
        if (!tail) {
            tail = url;
            prefix = "";
        }
        if (tail) {
            while ((tail.indexOf("//") > -1)) {
                tail = tail.replace("//", "/");
            }
            var x = tail.split('/');
            ret.absUrl.ref = prefix + "://";
            ret.absUrl.value = prefix + "://";
            for (var i = 0; i < x.length; i++) {
                ret.absUrl.value += "/" + x[i];
            }
            for (var i = 0; i < x.length - 1; i++) {
                ret.absUrl.ref += "/" + x[i];
            }
        }
        ret.absUrl.ref = fix(ret.absUrl.ref.replace(":////", "://"));
        ret.absUrl.value = ret.absUrl.value.replace(":////", "://");
        ret.absUrl.ref = fix(ret.absUrl.ref.replace(":///", "://"));
        ret.absUrl.value = ret.absUrl.value.replace(":///", "://");
        ret.relUrl.ref = fix(ret.absUrl.ref.substring(ret.host.length + 2, ret.absUrl.ref.length));
        ret.relUrl.value = fix(ret.absUrl.value.substring(ret.host.length + 2, ret.absUrl.value.length));
        if (ret.absUrl.ref.indexOf(ret.host) == -1) {
            ret.relUrl.ref = fix(ret.absUrl.ref.replace("://", ""));
            ret.relUrl.value = fix(ret.absUrl.value.replace("://", ""));
            ret.absUrl.ref = fix(ret.host + "/" + ret.relUrl.ref);
            ret.absUrl.value = fix(ret.host + "/" + ret.relUrl.value);
        }
        if (!isUrlOfPage(ret.absUrl.value)) {
            ret.absUrl.ref = fix(ret.absUrl.value);
            ret.absUrl.value = ret.absUrl.value + "/index.html";
        }
        if (!isUrlOfPage(ret.relUrl.value)) {
            ret.absUrl.ref = fix(ret.host + '/' + ret.relUrl.value);
            ret.absUrl.value = ret.host + '/' + ret.relUrl.value + "/index.html";
        }

        return ret;
    },
    combine:function combine(A, B) {

        var keys = Object.getOwnPropertyNames(B.prototype).concat(Object.keys(B));
            
        keys.forEach(k => {
            A["__proto__"][k] = B["prototype"][k] || B[k];
        });

        B.constructor.apply(A)
        return A;
    },
    urlGo:function (url) {
        window.history.pushState(url, url, url);
    },
    watchUrl:function (cb) {
        var oldUrl = undefined;
        function run() {
            if (oldUrl != window.location.href) {
                var path = window.location.pathname;
                cb(path);
                oldUrl = window.location.href;
            }

            setTimeout(run, 100);
        }
        run();
    },
    watchUrlOfApp: function (appDir, cb) {
        var oldUrl = undefined;
        function run() {
            if (oldUrl != window.location.href) {
                var path = window.location.pathname;
                if (path.toLocaleLowerCase().indexOf(appDir.toLocaleLowerCase() + "/")) {
                    var basePath = path.substring(appDir.length + 1, path.length);
                    cb(basePath);
                    oldUrl = window.location.href;
                }
            }

            setTimeout(run, 100);
        }
        run();
    },
    isAbsUrl:function (url) {
        return url.indexOf(window.location.protocol + "//" + window.location.host) == 0;
    },
    trimStartCharater: function (txt, trimCharater) {
        while (txt.length > trimStartCharater.length && txt[trimCharater.length] == trimCharater) {
            txt = txt.substring(trimStartCharater.length, txt.length);
        }
        return txt;
    },
    getService: function getService(name) {
        return angular.element(document.querySelector('[ng-controller]')).injector().get(name);
    }
}
export default utils;