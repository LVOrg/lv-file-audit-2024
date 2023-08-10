import datetime
import sys
import os
import pathlib
import time

sys.path.append(
    pathlib.Path(__file__).parent.parent.__str__()
)
import cy_kit
from cy_xdoc.services.apps import App
from cyx.base import DbConnect
import cy_docs

connector = cy_kit.singleton(DbConnect)
from cy_xdoc.models.files import DocUploadRegister
from cyx.models import FsFile
from cy_xdoc.models.apps import App

apps_context = connector.db("admin").doc(App)
list_of_apps = list(apps_context.context.aggregate().project(
    apps_context.fields.Name,
    apps_context.fields._id,
    apps_context.fields.Stats
))
from cy_xdoc.services.apps_stat import AppStatServices

app_stat_service = cy_kit.singleton(AppStatServices)

from cy_xdoc.models.apps import App

app_names = [app.Name for app in list_of_apps]


@cy_kit.loop_process([app.Name for app in list_of_apps if app.Stats is None])
def get_data(app_name: str):
    ret = app_stat_service.get_stat_of_app(app_name)
    return {app_name: ret}


quick_stat_data = get_data()
"""
Stats all app which never make stats before
"""
for x in quick_stat_data:
    app_name = list(x.keys())[0]
    update_data = x[app_name]
    apps_context.context.update(
        ((apps_context.fields.Stats == None) | (cy_docs.not_exists(apps_context.fields.Stats))) & (
                    apps_context.fields.Name == app_name),
        apps_context.fields.Stats << update_data
    )
for app in list_of_apps:
    app_stat_service.update_grant_stat(app_name=app.Name)