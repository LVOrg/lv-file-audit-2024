import dash_bootstrap_components as dbc
from dash import html,Dash, Input,Output,dcc
import dash

from dash.exceptions import PreventUpdate
def get_header(app:Dash):
    navs =[]
    for page in dash.page_registry.values():
        """page['name']} - {page['path']}", href=page["relative_path"]"""
        navs+=[dbc.NavItem(dbc.NavLink(
            page["name"],
            href=page["relative_path"]))
        ]
    navs+=[dbc.NavItem(dbc.NavLink("Help")),
                                    dbc.NavItem(dbc.NavLink("About"))]

    header = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        dbc.Col(dbc.NavbarBrand("Files", className="ms-2")),
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.Row(
                    [
                        dbc.NavbarToggler(id="navbar-toggler"),
                        dbc.Collapse(
                            dbc.Nav(
                                navs,
                                # make sure nav takes up the full width for auto
                                # margin to get applied
                                className="w-100",
                            ),
                            id="navbar-collapse",
                            is_open=False,
                            navbar=True,
                        ),
                    ],
                    # the row should expand to fill the available horizontal space
                    className="flex-grow-1",
                ),
            ],
            fluid=True,
        ),
        dark=True,
        color="dark",
    )



    return header