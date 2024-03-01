import dash
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Output, Input
from dash.dependencies import Input, Output
import json
import plotly.io as pio
import dash_bootstrap_components as dbc
from citizenvoice.dashboard.concept.graph_utils.graph_generator import Generator


path = "../resources/census-historic-population-borough.csv"
df = pd.read_csv(path)


year_to_col_name_mapping = {}

for colname in df.columns[2:]:
    year_to_col_name_mapping[colname[-4:]] = colname

pio.renderers.default = "browser"
# Building components
stylesheets = [dbc.themes.CYBORG]  # change this when we have our own CSS

app = Dash(__name__, external_stylesheets=stylesheets)
title = dcc.Markdown(children='# London population evolution by borough')
project_credits = dcc.Markdown(children='Citizen Voice Project')
input_year = dcc.Dropdown(id="select-year",
                          options=year_to_col_name_mapping,
                          multi=False,
                          value=2011,
                          style={'width': "70%"})

options_checklist = dcc.Checklist(
    id="options-checklist",
    options=["option1", "option2"]
)

graph = dcc.Graph(id='choropleth-map',
                  figure={},
                  style={
                      "margin": "0"
                  }
                  )  # this is the graph that we should be updating

# app.layout = dbc.Container([title, input_year, graph])
app.layout = dbc.Container([
    dbc.Row([title]),
    dbc.Row(children=[
        dbc.Col(children=[options_checklist], style={
            'width': "5"
        }),
        dbc.Col(children=[input_year, graph], style={
            'width': "10"
        })
    ]),
    dbc.Row(children=[
        dbc.Col(children=[project_credits]),
        html.Div()
    ])]

)


@app.callback(
    Output(graph, 'figure'),
    Input(input_year, component_property='value')
)
def update_graph(year):

    generator = Generator(df)
    fig = generator.create_choropleth(
        geojson_file="../resources/london_boroughs.json",
        statistic_column_name="Persons-"+str(year),
        area_column_name="Area Name"
    )
    fig.update_layout(width=600,
                      height=500)
    return fig


def run():
    if __name__ == '__main__':
        app.run_server(debug=True)


run()
