import pymysql
import sqlalchemy as sql

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# from app import app

layout_experiment = html.Div(
    [

		dcc.Tabs(
                    id="tabs",
                    value="new-experiment-tab",
                    children=[
                        dcc.Tab(
                            label="NEW EXPERIMENT",
                            value="new-experiment-tab",
                            children=[
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P(
                                                    "Date:",
                                                    className="input__heading",
                                                ),
                                                html.P(
                                                    id="new-experiment-date",
                                                    children=["NULL"],
                                                    className="oper__input",
                                                ),
                                            ],
                                            className="input__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "ID:",
                                                    className="input__heading",
                                                ),
                                                html.P(
                                                    id="new-experiment-id",
               										children=["NULL"],
                                                    className="oper__input",
                                                ),
                                            ],
                                            className="input__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "User(s):",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="new-experiment-user",
													options=[
													    {'label': 'User1', 'value': '1'},
													    {'label': 'User2', 'value': '2'},
													    {'label': 'User3', 'value': '3'}
													],
													multi=True,
                                                    placeholder="Select user(s)",
                                                    className="reag__select",
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "Tag(s):",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="new-experiment-tag",
													options=[
													    {'label': 'Tag1', 'value': '1'},
													    {'label': 'Tag2', 'value': '2'},
													    {'label': 'Tag3', 'value': '3'}
													],
													multi=True,
                                                    placeholder="Select tag(s)",
                                                    className="reag__select",
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "Comments:",
                                                    className="input__heading",
                                                ),
											    dcc.Textarea(
											        id='new-experiment-comment',
											        placeholder='Enter comment text here (Optional)',
											        style={'width': '100%', 'height': 300},
											    ),
                                            ],
                                            className="input__container",
                                        ),
                                        html.Div(
                                            [
                                                html.Button(
                                                    "SAVE",
                                                    id="new-experiment-btn-save",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                ),
                                              	html.Button(
                                                    "NEW EXPERIMENT",
                                                    id="new-experiment-btn-new",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                )
                                            ]
                                        ),
                                        dbc.Modal(
										    [
										        dbc.ModalHeader("NEW EXPERIMENT"),
										        dbc.ModalBody("This is the content of the modal"),
										        dbc.ModalFooter(
										            dbc.Button("Close", id="new-experiment-modal-btn-close", className="ml-auto")
										        ),
										    ],
										    id="new-experiment-modal",
										),
                                    ],
                                    className="container__1",
                                )
                            ],
                        ),
						dcc.Tab(
                            label="EDIT EXPERIMENT",
                            value="edit-experiment-tab",
                            children=[
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P(
                                                    "Date:",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="edit-experiment-date",
													options=[
													    {'label': 'User1', 'value': '1'},
													    {'label': 'User2', 'value': '2'},
													    {'label': 'User3', 'value': '3'}
													],
													multi=False,
                                                    placeholder="Select experiment date",
                                                    className="reag__select",
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "ID:",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="edit-experiment-id",
													options=[
													    {'label': 'User1', 'value': '1'},
													    {'label': 'User2', 'value': '2'},
													    {'label': 'User3', 'value': '3'}
													],
													multi=False,
                                                    placeholder="Select experiment id",
                                                    className="reag__select",
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "User(s):",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="edit-experiment-user",
													options=[
													    {'label': 'User1', 'value': '1'},
													    {'label': 'User2', 'value': '2'},
													    {'label': 'User3', 'value': '3'}
													],
													multi=True,
                                                    placeholder="Select user(s)",
                                                    className="reag__select",
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "Tag(s):",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="edit-experiment-tag",
													options=[
													    {'label': 'Tag1', 'value': '1'},
													    {'label': 'Tag2', 'value': '2'},
													    {'label': 'Tag3', 'value': '3'}
													],
													multi=True,
                                                    placeholder="Select tag(s)",
                                                    className="reag__select",
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "Comments:",
                                                    className="input__heading",
                                                ),
											    dcc.Textarea(
											        id='edit-experiment-comment',
											        placeholder='Enter comment text here (Optional)',
											        style={'width': '100%', 'height': 300},
											    ),
                                            ],
                                            className="input__container",
                                        ),
                                        html.Div(
                                            [
                                                html.Button(
                                                    "LOAD",
                                                    id="edit-experiment-btn-load",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                ),
                                              	html.Button(
                                                    "SAVE",
                                                    id="edit-experiment-btn-save",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                )
                                            ]
                                        ),
                                        dbc.Modal(
										    [
										        dbc.ModalHeader("EDIT EXPERIMENT"),
										        dbc.ModalBody("This is the content of the modal"),
										        dbc.ModalFooter(
										            dbc.Button("Close", id="edit-experiment-modal-btn-close", className="ml-auto")
										        ),
										    ],
										    id="edit-experiment-modal",
										),
                                    ],
                                    className="container__1",
                                )
                            ],
                        ),
						dcc.Tab(
                            label="EDIT USER",
                            value="edit-user-tab",
                            children=[
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P(
                                                    "ID:",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="edit-user-id",
													options=[
													    {'label': '1', 'value': '1'},
													    {'label': '2', 'value': '2'},
													    {'label': '3', 'value': '3'}
													],
													multi=False,
                                                    placeholder="Select user id",
                                                    className="reag__select",
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "Name:",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="edit-user-name",
													options=[
													    {'label': 'User1', 'value': 'User1'},
													    {'label': 'User2', 'value': 'User2'},
													    {'label': 'User3', 'value': 'User3'}
													],
													multi=False,
                                                    placeholder="Select user name",
                                                    className="reag__select",
                                                ),
                                                dcc.Input(
                                                	id='edit-user-name-input',
                                                	type='text',
                                                	placeholder='Enter new name here',
                                                	style={"margin-top": "0.5%"},
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "Comments:",
                                                    className="input__heading",
                                                ),
											    dcc.Textarea(
											        id='edit-user-comment',
											        placeholder='Enter comment text here (Optional)',
											        style={'width': '100%', 'height': 300},
											    ),
                                            ],
                                            className="input__container",
                                        ),
                                        html.Div(
                                            [
                                                html.Button(
                                                    "NEW USER",
                                                    id="edit-user-btn-new",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                ),
                                              	html.Button(
                                                    "SAVE",
                                                    id="edit-user-btn-save",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                ),
                                                html.Button(
                                                    "LOAD USER",
                                                    id="edit-user-btn-load",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                ),
                                            ]
                                        ),
                                        dbc.Modal(
										    [
										        dbc.ModalHeader("EDIT USER"),
										        dbc.ModalBody("This is the content of the modal"),
										        dbc.ModalFooter(
										            dbc.Button("Close", id="edit-user-modal-btn-close", className="ml-auto")
										        ),
										    ],
										    id="edit-user-modal",
										),
                                    ],
                                    className="container__1",
                                )
                            ],
                        ),
						dcc.Tab(
                            label="EDIT TAG",
                            value="edit-tag-tab",
                            children=[
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P(
                                                    "ID:",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="edit-tag-id",
													options=[
													    {'label': '1', 'value': '1'},
													    {'label': '2', 'value': '2'},
													    {'label': '3', 'value': '3'}
													],
													multi=False,
                                                    placeholder="Select tag id",
                                                    className="reag__select",
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    "Name:",
                                                    className="input__heading",
                                                ),
                                                dcc.Dropdown(
                                                    id="edit-tag-name",
													options=[
													    {'label': 'Tag1', 'value': 'Tag1'},
													    {'label': 'Tag2', 'value': 'Tag2'},
													    {'label': 'Tag3', 'value': 'Tag3'}
													],
													multi=False,
                                                    placeholder="Select tag name",
                                                    className="reag__select",
                                                ),
                                                dcc.Input(
                                                	id='edit-tag-name-input',
                                                	type='text',
                                                	placeholder='Enter new tag here',
                                                	style={"margin-top": "0.5%"},
                                                ),
                                            ],
                                            className="dropdown__container",
                                        ),
                                        html.Div(
                                            [
                                                html.Button(
                                                    "NEW TAG",
                                                    id="edit-tag-btn-new",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                ),
                                              	html.Button(
                                                    "SAVE",
                                                    id="edit-tag-btn-save",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                ),
                                                html.Button(
                                                    "LOAD TAG",
                                                    id="edit-tag-btn-load",
                                                    className="submit__button",
                                                    style={"margin-right": "2.5%"},
                                                ),
                                            ]
                                        ),
                                        dbc.Modal(
										    [
										        dbc.ModalHeader("EDIT TAG"),
										        dbc.ModalBody("This is the content of the modal"),
										        dbc.ModalFooter(
										            dbc.Button("Close", id="edit-tag-modal-btn-close", className="ml-auto")
										        ),
										    ],
										    id="edit-tag-modal",
										),
                                    ],
                                    className="container__1",
                                )
                            ],
                        ),
                	],
            		className="tabs__container",
                )
    ],
    className="app__container"
    )


