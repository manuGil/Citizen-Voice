import pandas as pd


class Cleaner:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

    def drop_columns(self, column_indices: list):
        return self.dataframe.drop(column_indices)
    # eventually use args and kwargs

