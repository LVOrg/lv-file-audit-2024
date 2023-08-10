import os
import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
from cy_ui.main_page import get_header
import dash_uploader as du
from  cyx.common import config
if config.ui:
    app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR],url_base_pathname=f'/{config.ui}/',use_pages=True)
else:
    app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR], use_pages=True)

from dash import Dash, html
root_app_dir = pathlib.Path(__file__).parent.parent.__str__()
header = get_header(app)
tmp_upload_dir = config.tmp_upload_dir
if tmp_upload_dir[0:2]=="./":
    tmp_upload_dir = os.path.abspath(
        os.path.join(root_app_dir,tmp_upload_dir[2:])
    )
if not os.path.isdir(tmp_upload_dir):
    os.makedirs(tmp_upload_dir,exist_ok=True)
du.configure_upload(app, tmp_upload_dir)
app.layout = html.Div(
    [header, dash.page_container]
)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run_server(host="0.0.0.0", debug=True, port=8081)