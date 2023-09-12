class api {
    static serverApIHostUrl = ""
    static _onBeforeCall = undefined
    static _onAfterCall = undefined
    static _onError = undefined
    static _onAuthRequire = undefined
    static storeAccessToken(tk) {
        window.localStorage['token'] = tk;
    }
    static getToken() {
        return window.localStorage['token']
    }
    static setUrl(url) {
        api.serverApIHostUrl = url
    }
    static getUrl() {
        return api.serverApIHostUrl;
    }
    static onBeforeCall(callback) {
        api._onBeforeCall = callback;
        return api;
    }
    static onAfterCall(callback) {
        api._onAfterCall = callback;
        return api;
    }
    static onAuthRequire(callback) {
        api._onAuthRequire = callback;
        return api;
    }
    static onError(callback) {
        api._onError = callback;
        return api;
    }
    static async get(apiPath) {
        var url = this.serverApIHostUrl + "/" + apiPath;
        return await fetch(url)
            .then((response) => {
                return response.json();
            });

    }
    static async post(apiPath, data,noMask) {
        var sender = undefined;
        if (!noMask && api._onBeforeCall) {
            sender = await api._onBeforeCall();
        }
        try {
            var ret = await api.__post__(apiPath, data);
            if (!noMask && api._onAfterCall) {
                await api._onAfterCall(sender)
            }
            return ret;
        }
        catch (e) {
            
            if (!noMask && api._onAfterCall) {
                await api._onAfterCall(sender)
            }
            if (api._onError) {
                await api._onError(e)
            }
        }
    }
    static async __post__(apiPath, data) {
        debugger
        var url = this.serverApIHostUrl + "/" + apiPath;
        function checkHasFile() {
            var retData = {}
            var files = undefined
            var keys = Object.keys(data);
            for (var i = 0; i < keys.length; i++) {
                var val = data[keys[i]];
                if (val instanceof File) {
                    if (!files) files = {}
                    files[keys[i]] = val
                }
                else {
                    retData[keys[i]] = val
                }
            }
            return {
                data: retData,
                files: files
            }
        }
        var checkData = checkHasFile()
        if (!checkData.files) {
           
            var fetcher = await fetch(url, {
                method: 'POST',
                //mode: 'no-cors', // this is to prevent browser from sending 'OPTIONS' method request first
                //credentials: "include",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + api.getToken()
                },
                body: JSON.stringify(data)
            });

            if (fetcher.status >= 200 && fetcher.status < 300) {
                return await fetcher.json();

            }
            else {
                if (fetcher.status == 401) {
                    if (api._onAuthRequire) {
                        await api._onAuthRequire();
                    }
                }
                var err = await fetcher.json()
                throw (err)
            }
            
        }
        else {
            var formData = new FormData()
            var fileKeys = Object.keys(checkData.files)
            for (var i = 0; i < fileKeys.length; i++) {
                formData.append(fileKeys[i], checkData.files[fileKeys[i]]);
            }
            formData.append('data', JSON.stringify(checkData.data))

            var fetcher = await fetch(url, {
                method: 'POST',
                body: formData
            });
            return await fetcher.json();
        }

    }
    static async formPost(apiPath, data, noMask) {
        var url = this.serverApIHostUrl + "/" + apiPath;
        var formData = new FormData()
        var keys = Object.keys(data)
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i]
            var val = data[key]
            formData.append(key, val);
            
        }
        var sender = undefined;
        if (!noMask && api._onBeforeCall) {
            sender = await api._onBeforeCall();
        }
        try {
            var fetcher = await fetch(url, {
                method: 'POST',
                body: formData
            });
            if (!noMask && api._onAfterCall) {
                await api._onAfterCall(sender)
            }
            if (fetcher.status >= 200 && fetcher.status < 300) {
                return await fetcher.json();

            }
            else {
                var err = await fetcher.json()
                throw (err)
            }
            
        }
        catch (e) {

            if (!noMask && api._onAfterCall) {
                await api._onAfterCall(sender)
            }
            if (api._onError) {
                await api._onError(e)
            }
            throw (e)
        }
    }
}
export default api