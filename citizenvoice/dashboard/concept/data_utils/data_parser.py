import json

import pandas as pd


class Parser:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

    def combine_df_with_geojson(self, geojson_file):
        geojson_data = json.load(open(geojson_file, "r"))
        geojson_features = geojson_data['features']

        # map ids
        id_mapping_dict = {}
        for feature in geojson_features:
            feature['id'] = feature['properties']['id']
            id_mapping_dict[feature['properties']['name']] = feature['id']

        combined_df = self.dataframe.copy()

        combined_df["id"] = combined_df["Area Name"].apply(lambda x: id_mapping_dict[x])
        return combined_df
