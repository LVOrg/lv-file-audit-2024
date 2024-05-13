import datetime

import traceback

from cyx.repository import Repository


class ProcessManagerService:
    def __init__(self):
        pass

    def submit(self, data, app_name, action_type):
        if data.ProcessInfo is None:
            Repository.files.app(app_name).context.update(
                Repository.files.fields.id == data.id,
                Repository.files.fields.ProcessInfo << {action_type: dict(

                    IsError=False,
                    Error="",
                    UpdateTime=datetime.datetime.utcnow(),

                )}
            )
        else:
            Repository.files.app(app_name).context.update(
                Repository.files.fields.id == data.id,
                getattr(Repository.files.fields.ProcessInfo, action_type) << dict(
                    IsError=False,
                    Error="",
                    UpdateTime=datetime.datetime.utcnow(),

                )
            )

    def submit_error(self, data, app_name, action_type, error):

        if not isinstance(error,str):
            error = traceback.format_exc()
        if data.ProcessInfo is None:
            Repository.files.app(app_name).context.update(
                Repository.files.fields.id == data.id,
                Repository.files.fields.ProcessInfo << {action_type: dict(

                    IsError=True,
                    Error=error,
                    UpdateTime=datetime.datetime.utcnow(),

                )}
            )
        else:
            Repository.files.app(app_name).context.update(
                Repository.files.fields.id == data.id,
                getattr(Repository.files.fields.ProcessInfo, action_type) << dict(
                    IsError=True,
                    Error=error,
                    UpdateTime=datetime.datetime.utcnow(),

                )
            )
