import enig
import enig_frames.config
import sys

# from werkzeug import debug

import fasty
import pathlib
# fasty.load_config(str(pathlib.Path(__file__).parent), "uvicorn.error")
import fasty.JWT


import os
os.environ['config.db.host']='172.16.7.25'
os.environ['config.db.port']='27018'
os.environ['config.db.username']=''
os.environ['config.db.password']=''
os.environ['config.db.authMechanism']=''
os.environ['config.admin_db_name']='enigma-media'
import uvicorn
configuration:enig_frames.config.Configuration = enig.create_instance(enig_frames.config.Configuration)

if __name__ == "__main__":

    uvicorn.run(
        "api_app:app",
        host=configuration.config.binding_ip,
        port=configuration.config.binding_port,
        workers=1,
        ws='websockets',
        ws_max_size=16777216*1024,
        backlog=1000,
        # interface='WSGI',
        timeout_keep_alive=True,
        lifespan='on',

        debug=True,
        # reload=False,

    )
