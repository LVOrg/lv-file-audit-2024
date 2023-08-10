import { redirect, urlWatching, getModule } from "../js/ui/core.js"

async function startRoute(me) {
   
    await urlWatching($("head base").attr("href"), async (_path) => {
        debugger;
        var path=_path;
        var base_url=$("head base").attr("href");
        var sub_dir=base_url.substring(window.location.origin.length,base_url.length);
        if (sub_dir!='/')
        {
            path=[];
            for(i=1;i<_path.length;i++){
                path.push(_path[i]);
            }

        }
        console.log(path);

        var bodyContainer = $("#body")[0];
        var loadPath = "./apps/index.js" //Mặc định lấy trang chủ
        if (path.length > 1) {
            loadPath = "";
            for (var i = 1; i < path.length; i++) {
                loadPath += "/" + path[i]
            }
            loadPath += "/index.js"; // mọi controller nằm trong index.js
            loadPath = "." + loadPath;
        }
        $(bodyContainer).empty();
        var view = await me.loadView(loadPath);
        //await view.doEditApp(path[2]);
        await view.render(bodyContainer);
        await view.init();
        
    })
}
export { startRoute }