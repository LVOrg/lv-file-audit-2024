import { } from "./angular.js"
import { BaseView, View } from "./core.js";
var serverApIHostUrl = "";
function setServerApiHostUrl(url) {
    serverApIHostUrl = url;
}
class BaseScope extends BaseView {
    model = {}
    constructor() {
        super();

    }

    async get(apiPath) {
        var url = serverApIHostUrl + "/" + apiPath;
        return await fetch(url)
            .then((response) => {
                return response.json();
            });

    }
    async post(apiPath, data) {
        var url = serverApIHostUrl + "/" + apiPath;
        var fetcher = await fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return await fetcher.json();

    }
    
}
export { BaseScope, View, setServerApiHostUrl }