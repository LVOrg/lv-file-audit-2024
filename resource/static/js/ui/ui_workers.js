var __urlOfRunnerWorker = undefined;
var __urlOfEmptyWorker = undefined;
class ui_worker_task {

    worker;
    _fn;
    _args;
    _resolve;
    _reject;
    _isAsync;
    _ex;
    _result;
    constructor() {
        var me = this;

        if (__urlOfEmptyWorker == undefined) {
            var blob = new Blob(
                ["onmessage=function(e){postMessage(e.data);}"],
                {
                    type: "text/plain;charset=utf-8"
                }
            );
            __urlOfEmptyWorker = URL.createObjectURL(blob);
        }
        var urlOfEmpty = __urlOfEmptyWorker;
        var x = {};
        this.worker = new Worker(urlOfEmpty);
        this.worker.addEventListener("message", e => {
            if (e.data.isStart) {
                try {
                    var args = [];
                    args.push(me);
                    for (var i = 0; i < me._args.length; i++) {
                        args.push(me._args[i]);

                    }

                    var ret = me._fn.apply(me, args);

                    me._resolve(ret);
                    me.worker.terminate();
                } catch (e) {
                    me._reject(e);
                    me.worker.terminate();
                }
            }
            else if (e.data.waiting) {
                var resolve = (r) => {
                    me._result = r;
                    me.worker.postMessage({ isDone: true });
                }
                var reject = () => { };
                try {
                    var args = [];
                    args.push(me);
                    args.push(resolve);
                    args.push(reject);
                    for (var i = 2; i < me._args.length; i++) {
                        args.push(me._args[i]);

                    }
                    var ret = me._fn.apply(me, args);

                } catch (e) {
                    me.worker.postMessage({ isError: true });
                    me._ex = e;

                }
            }
            else if (e.data.isDone) {
                me._resolve(me._result);
                me.worker.terminate();
            }
            else if (e.data.isError) {
                me._reject(me._ex);
                me.worker.terminate();
            }
        });
    }
    start(fn) {
        this._fn = fn;
        var me = this;
        function run() {

            me._args = arguments;
            me.worker.postMessage({ isStart: true });
            return new Promise(function (resolve, reject) {
                me._resolve = resolve;
                me._reject = reject;

            });
        }
        return run;
    }
    startAsync(fn) {
        this._fn = fn;
        var me = this;
        this._isAsync = true;
        function run() {

            me._args = arguments;
            me.worker.postMessage({ waiting: true });
            return q.html.createPromise((resolve, reject) => {
                me._resolve = resolve;
                me._reject = reject;

            });
        }
        return run;
    }
}
var ui_workers = {
    __urlOfRunnerWorker: undefined,
    __urlOfEmptyWorker: undefined,
    createUrlOfFunc: function (fn) {
        var fnText = fn.toString();
        var _fx = `onmessage =function(e){ 
                            var ret=undefined;
                            if(e.data.start) {
                               try { 
                                var fn = ${fnText}; 
                                ret = fn.apply(this, e.data.params);
                                 postMessage({stop:true,result:ret});
                               }
                               catch(ex){
                                    postMessage({error:true,exception:ex.toString()});
                               }
                               
                            }
                            
                        }`;

        var blob = new Blob(
            [_fx],
            {
                type: "text/plain;charset=utf-8"
            }
        );
        return URL.createObjectURL(blob);
    },
    create: function (fn) {
        if (workers.__urlOfRunnerWorker == undefined) {
            workers.__urlOfRunnerWorker = workers.createUrlOfFunc(fn);
        }
        var url = workers.__urlOfRunnerWorker;

        var ret = function () {
            var args = arguments;
            var params = [];
            for (var i = 0; i < args.length; i++) {
                params.push(args[i]);
            }
            return q.html.createPromise((resolve, reject) => {

                var w = new Worker(url);
                w.addEventListener("message", e => {
                    if (e.data.stop) {
                        resolve(e.data.result);
                        w.terminate();
                    }
                });
                w.addEventListener("message", e => {
                    if (e.data.error) {
                        reject(e.data.exception);
                        w.terminate();
                    }
                });
                w.postMessage({ start: true, params: params });
            });
        }
        return ret;

    },
    task: ui_worker_task ,
    newTask: function () {
        return new ui_worker_task();

    }

};
export { ui_workers}