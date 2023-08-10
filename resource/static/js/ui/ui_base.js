class api {
    serverApIHostUrl=""
    static setUrl(url) {
        serverApIHostUrl = url
    }
    static async post(apiPath, data) {
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
    static async get(apiPath) {
        var url = serverApIHostUrl + "/" + apiPath;
        return await fetch(url)
            .then((response) => {
                return response.json();
            });

    }
}