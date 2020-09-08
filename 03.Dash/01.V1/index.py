import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app # calls the app

from apps import app_experiment # input data for the experiment (admin stuff) and edit existing experiment data
from apps import app_sensor_readout # show sensor data. This is the main feature
from apps import app_sensor_control # show sensor data. This is the main feature

app.layout = html.Div(
	[
	    html.Div(
	    [
	        # html.Img(src="assets/logo.png", className="app__logo"),
	        html.Img(src=app.get_asset_url('logo.png'), className="app__logo"),
	        html.H4("Version 2020.08.003", className="header__text"),
	    ],
	    className="app__header",
		),
		dcc.Location(id='url', refresh=False),
		html.Div(id='page-content')
	]
	)

index_page = html.Div(
				[
					html.Div(
						[
							html.P("\
								Welcome to the control program of the Fast Neutron Laboratory's Neutron Generator. ",
								style={"margin-left": "10%"},
								className='header__text'),
							html.P("\
								You can find the manual for the control here (insert PDF). ",
								style={"margin-left": "10%"},
								className='row'),
						],
                    className="one-third column"
					),
					html.Div(
						[
							html.H3("Navigation", style={"margin-bottom": "5%", "letter-spacing": "0.23rem"},),
							html.Hr(),
							html.A('Go to Experiment editor', href='/apps/app_experiment', target="_blank", style={"font-size": "1.6em"}),
							html.Hr(),
							html.A('Go to Sensor readout', href='/apps/app_sensor_readout', target="_blank", style={"font-size": "1.6em"}),
							html.Br(),
							html.A('Go to Sensor control', href='/apps/app_sensor_control', target="_blank", style={"font-size": "1.6em"}),
							html.Hr(),
							html.A('Go to Operation report', href='/apps/app_experiment', target="_blank", style={"font-size": "1.6em"}),
						],
                    className="one-third column"
					),
					html.Div(
						[

						],
                    className="one-third column"
					),
					html.Br()
				],
				className="row flex-display"
			)

# Update the index
@app.callback(Output('page-content', 'children'),
			  [Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/apps/app_experiment':
		return app_experiment.layout_experiment
	elif pathname == '/apps/app_sensor_readout':
		return app_sensor_readout.layout_sensor_readout
	elif pathname == '/apps/app_sensor_control':
		return app_sensor_control.layout_sensor_control
	else:
		return index_page
	# You could also return a 404 "URL not found" page here

if __name__ == "__main__":
    app.run_server(debug=True, port=5000, host='0.0.0.0') # at PSI
    # app.run_server(debug=True) # at home