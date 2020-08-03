import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app # calls the app

from apps import app_experiment # input data for the experiment (admin stuff) and edit existing experiment data

app.layout = html.Div(
	[
	    html.Div(
	    [
	        # html.Img(src="assets/logo.png", className="app__logo"),
	        html.Img(src=app.get_asset_url('logo.png'), className="app__logo"),
	        html.H4("Version 2020.07.000", className="header__text"),
	    ],
	    className="app__header",
		),
		dcc.Location(id='url', refresh=False),
		html.Div(id='page-content')
	]
	)

index_page = html.Div([
	html.A('Experiment editor', href='/apps/app_experiment', target="_blank"),
	html.Br()
])

# Update the index
@app.callback(Output('page-content', 'children'),
			  [Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/apps/app_experiment':
		return app_experiment.layout_experiment
	else:
		return index_page
	# You could also return a 404 "URL not found" page here

if __name__ == "__main__":
    app.run_server(debug=True)