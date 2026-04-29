import numpy as np
import pandas as pd
from numpy import abs
from numpy import log
from numpy import sign
from scipy.stats import rankdata
import seaborn as sns
import matplotlib.pyplot as plt

# def get_model(df, strategy, window, threshold):
#     factor=Backtests(df)
#     factor.z_score_model(window, threshold, strategy)
    # df['model002']=factor.model002()
    # df['model003']=factor.model003()

class BacktestModelSample(object):

    def __init__(self, df):
        self.df = df.copy()
        self.price = df['price'] 
        self.factor = df.drop(columns=['price']) 

    # [(factor - ma) / std]
    def zscore_model(self, strategy, window, threshold):

        """
        "Normalized Moving-Average (Dynamic) Delta" 

        Extracts moving-average delta change.
        """

        df = self.df.copy()
        df['chg'] = self.price.pct_change()

        # Calculate z-score
        ''' One line Formulaic Model Integration '''
        df['ma'] = self.factor.rolling(window).mean()
        df['sd'] = self.factor.rolling(window).std()
        df['Z-Score'] = (self.factor.iloc[:,0] - df['ma']) / df['sd']

        # Entry / Exit strategies available for current model  
        if strategy == 'zscore_momentum_buy':
            df['pos'] = np.where(df['Z-Score'] > threshold, 1, 0)
        elif strategy == 'zscore_momentum_sell':
            df['pos'] = np.where(df['Z-Score'] < threshold, -1, 0)
        elif strategy == 'zscore_reversion_buy':
            df['pos'] = np.where(df['Z-Score'] < threshold, 1, 0)
        elif strategy == 'zscore_reversion_sell':
            df['pos'] = np.where(df['Z-Score'] > threshold, -1, 0)

        # Backtest calculation 
        df['pos_t-1'] = df['pos'].shift(1)
        df['trade'] = abs(df['pos_t-1'] - df['pos'])
        df['pnl'] = df['pos_t-1'] * df['chg'] - df['trade'] * 0.07 / 100 # Bybit 0.55bps (fee) + 0.15bps (slippage / misc.) 
        df['cumu_pnl'] = df['pnl'].cumsum()
        df['dd'] = df['cumu_pnl'].cummax() - df['cumu_pnl']

        # Metrics information extraction
        AR = round(df['pnl'].mean() * 365*24,3) 
        SR = round(df['pnl'].mean() / df['pnl'].std() * np.sqrt(365*24),3) # hourly setting 
        MDD = round(df['dd'].max(),3)
        CR = round(AR / MDD,3)
        EXECUTIONS = df['trade'].sum()

        return pd.Series(
            [window,round(threshold,3),AR,MDD,SR,CR,EXECUTIONS],
            index=['window','threshold','AR','MDD','SR','CR','EXECUTIONS']
        )
    
    # [(factor{t} - factor{t-1}) / std]
    def normdelta_model(self,strategy,window,threshold):
        """
        "Normalized Raw Delta" 

        Extracts raw delta change.
        """

        df = self.df.copy()
        df['chg'] = self.price.pct_change()

        # Calculate normalized-raw-delta
        ''' One line Formulaic Model Integration '''
        df['sd'] = self.factor.rolling(window).std()
        df['Delta'] = self.factor.diff()
        df['Norm_Delta'] = df['Delta'] / df['sd']

        # Entry / Exit strategies available for current model  
        if strategy == 'normdelta_momentum_buy':
            df['pos'] = np.where(df['Norm_Delta'] > threshold, 1, 0)
        elif strategy == 'normdelta_momentum_sell':
            df['pos'] = np.where(df['Norm_Delta'] < threshold, -1, 0)
        elif strategy == 'normdelta_reversion_buy':
            df['pos'] = np.where(df['Norm_Delta'] < threshold, 1, 0)
        elif strategy == 'normdelta_reversion_sell':
            df['pos'] = np.where(df['Norm_Delta'] > threshold, -1, 0)

        # Backtest calculation 
        df['pos_t-1'] = df['pos'].shift(1)
        df['trade'] = abs(df['pos_t-1'] - df['pos'])
        df['pnl'] = df['pos_t-1'] * df['chg'] - df['trade'] * 0.07 / 100 # Bybit 0.55bps (fee) + 0.15bps (slippage / misc.) 
        df['cumu_pnl'] = df['pnl'].cumsum()
        df['dd'] = df['cumu_pnl'].cummax() - df['cumu_pnl']

        # Metrics information extraction
        AR = round(df['pnl'].mean() * 365*24,3) 
        SR = round(df['pnl'].mean() / df['pnl'].std() * np.sqrt(365*24),3) # hourly setting 
        MDD = round(df['dd'].max(),3)
        CR = round(AR / MDD,3)
        EXECUTIONS = df['trade'].sum()

        return pd.Series(
            [window,round(threshold,3),AR,MDD,SR,CR,EXECUTIONS],
            index=['window','threshold','AR','MDD','SR','CR','EXECUTIONS']
        )

    def sma_model(self,strategy,window,threshold):
        """
        "Momentum"

        Extracts momentum information.
        """

        df = self.df.copy()
        df['chg'] = self.price.pct_change()

        # Calculate normalized-raw-delta
        ''' One line Formulaic Model Integration '''
        df['ma'] = self.factor.rolling(window).mean()
        df['ma_model'] = self.factor.iloc[:,0] / df['ma'] -1 
        # Standardize the ma-model thresholds
        ma_model_mean = df['ma_model'].mean()
        ma_model_std = df['ma_model'].std()
        df['scaled_ma_model'] = (df['ma_model'] - ma_model_mean) / ma_model_std

        # Entry / Exit strategies available for current model  
        if strategy == 'sma_momentum_buy':
            df['pos'] = np.where(df['scaled_ma_model'] > threshold, 1, 0)
        elif strategy == 'sma_reversion_sell':
            df['pos'] = np.where(df['scaled_ma_model'] < threshold, -1, 0)
        elif strategy == 'sma_momentum_sell':
            df['pos'] = np.where(df['scaled_ma_model'] < threshold, -1, 0)
        elif strategy == 'sma_reversion_buy':
            df['pos'] = np.where(df['scaled_ma_model'] < threshold, 1, 0)

        # Backtest calculation 
        df['pos_t-1'] = df['pos'].shift(1)
        df['trade'] = abs(df['pos_t-1'] - df['pos'])
        df['pnl'] = df['pos_t-1'] * df['chg'] - df['trade'] * 0.07 / 100 # Bybit 0.55bps (fee) + 0.15bps (slippage / misc.) 
        df['cumu_pnl'] = df['pnl'].cumsum()
        df['dd'] = df['cumu_pnl'].cummax() - df['cumu_pnl']

        # Metrics information extraction
        AR = round(df['pnl'].mean() * 365*24,3) 
        SR = round(df['pnl'].mean() / df['pnl'].std() * np.sqrt(365*24),3) # hourly setting 
        MDD = round(df['dd'].max(),3)
        CR = round(AR / MDD,3)
        EXECUTIONS = df['trade'].sum()

        return pd.Series(
            [window,round(threshold,3),AR,MDD,SR,CR,EXECUTIONS],
            index=['window','threshold','AR','MDD','SR','CR','EXECUTIONS']
        )
