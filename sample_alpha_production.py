from subsystems.factor_1 import Factor1
from database.postgres.postgres_client import PostgresClient
from utils.math_utils import round_up_hundreds
from pprint import pprint, pformat
from datetime import datetime
from copy import deepcopy
import pandas as pd 
import numpy as np 
import requests
import logging
import time 

logger = logging.getLogger(__name__)
logger.info(f"Logger Initiated: {logger}")

class Factor2(Factor1):
    metadata = {
        "model_1": {
            "strat": "lb_zscore_mom",
            "window": 1200,
            "threshold": 0.5
        },
        "model_2": {
            "strat": "lb_zscore_mom",
            "window": 600,
            "threshold": 0.8
        }
    }

    def __init__(self, db_config):
        ### Metadata 
        self.metadata = deepcopy(self.metadata) # Immutable class level attribute 
        self.model_1 = self.metadata["model_1"]
        self.model_2 = self.metadata["model_2"]

        ### Factor Data Access 
        self.topic = "glassnode|addresses/profit_count?a=BTC&i=1h"
        self.alpha_col = "v"
        self.factor_id = "factor_2"

        ### Database Params
        self.db_config = db_config
        self.encoding_db_params = ["encoding_db", "cybotrade", "topic_encoding"] 
        self.history_db_params = ["cybotrade_history",None,None]
        self.stats_db_params = ["factor_stats",None,None]

    def get_factor_db(self):
        '''
        - Extract needed dfs : Detects "topic" and "alpha_col" automatically 
        - Creates standard alpha_df containing information needed 
        - Pre-processing : standardize 'start_time' columns for merging before-hand // rename alpha_col to x_1, x_2, ...
        '''
        df_1 = self.get_sql_history_db() # Attches "topic" entry point at instance level (self.topic)

        df_1 = df_1[["start_time", self.alpha_col]] # Fixed start_time col and 
        df_1 = df_1.rename(columns = {self.alpha_col: "x_1"})

        df = df_1
        # df = pd.merge(df_1, df_2, how="inner", on="start_time")
        return df
    
    def strat_1(self):
        strat_id = "strat_1"
        df = self.get_factor_db()

        ### Model Engineering 
        df["x1_ma"] = df["x_1"].rolling(self.model_1["window"]).mean()
        df["x1_std"] = df["x_1"].rolling(self.model_1["window"]).std() 
        df["model"] = (df["x_1"] - df["x1_ma"]) / df["x1_std"]
        df["pos"] = np.where(df["model"] > self.model_1["threshold"], 1, 0) 

        quarter_df = df.tail(2200)
        signal = df["pos"].iloc[-1]
        return strat_id, quarter_df, signal

    def strat_2(self):
        strat_id = "strat_2"
        df = self.get_factor_db()

        ### Model Engineering 
        df["x1_ma"] = df["x_1"].rolling(self.model_2["window"]).mean()
        df["x1_std"] = df["x_1"].rolling(self.model_2["window"]).std() 
        df["model"] = (df["x_1"] - df["x1_ma"]) / df["x1_std"]
        df["pos"] = np.where(df["model"] > self.model_2["threshold"], 1, 0) 

        quarter_df = df.tail(2200)
        signal = df["pos"].iloc[-1]
        return strat_id, quarter_df, signal
    
    def compute_signal_distribution(self):
        ### Compiles all strategies 
        all_strats= [self.strat_1(), self.strat_2()]

        signal_distribution = [] 
        quarter_df_list = [] 
        alpha_id_list= [] 
        for strat_id, quarter_df, signal in all_strats:
            signal_distribution.append(signal) # No strict numpy typing accounts for continuous strategy signal types (int / float)
            quarter_df_list.append(quarter_df)
            alpha_id = f"{self.factor_id}__{strat_id}" 
            alpha_id_list.append(alpha_id)
        return signal_distribution, quarter_df_list, alpha_id_list