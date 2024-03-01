import pandas as pd
import plotly.express as px
from citizenvoice.dashboard.concept.data_utils.data_parser import Parser
from citizenvoice.dashboard.concept.data_utils.data_cleaner import Cleaner
import json

pd.options.mode.chained_assignment = None


class Generator:
    def __init__(self, df: pd.DataFrame):
        self.dataframe = df

    def create_choropleth(self, geojson_file, statistic_column_name,
                          area_column_name):  # eventually use kwargs to configure graph settings
        """
        Uses geojson file provided to create a choropleth map using the statistic given by column_name
        """

        geojson = json.load(open(geojson_file, "r"))

        population_data = Cleaner(self.dataframe).drop_columns([33, 34, 35])

        df = population_data[[area_column_name, statistic_column_name]]

        dict = {}

        for feature in geojson['features']:
            feature['id'] = feature["properties"]["id"]
            dict[feature["properties"]["name"]] = feature["id"]

        df["id"] = df[area_column_name].apply(lambda x: dict[x])

        fig = px.choropleth_mapbox(df,
                                   locations="id",
                                   geojson=geojson,
                                   color=statistic_column_name,
                                   hover_name=area_column_name,
                                   mapbox_style="open-street-map",
                                   center={
                                       'lat': 51.5,
                                       'lon': -0.11
                                   },
                                   zoom=8,
                                   opacity=1
                                   )

        return fig
